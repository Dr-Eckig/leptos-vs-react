# python3 json-to-excel.py playwright-kanban/results kanban-performance-results.xlsx

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape, quoteattr
from zipfile import ZIP_DEFLATED, ZipFile


XLSX_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
MAX_EXCEL_ROWS = 1_048_576
MAX_EXCEL_COLUMNS = 16_384
MAX_CELL_TEXT_LENGTH = 32_767
MAX_HEADER_TEXT_LENGTH = 255
RESULT_SHEET_NAME = "Results"
RESULT_COLUMNS = ["run", "framework", "browser", "action", "zeit"]


@dataclass
class Sheet:
    name: str
    columns: list[str]
    rows: list[dict[str, Any]]
    sheet_id: int = 0
    table_name: str = ""
    headers: list[str] | None = None
    ref: str = ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert JSON files to one Excel table in a .xlsx workbook.",
    )
    parser.add_argument("input", help="JSON file or folder containing JSON files")
    parser.add_argument("output", nargs="?", help="Output .xlsx file")
    parser.add_argument("-o", "--out", dest="output_option", help="Output .xlsx file")
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only read JSON files directly inside the input folder",
    )
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output_option or args.output or default_output_path(input_path)).resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    json_files = collect_json_files(input_path, recursive=not args.no_recursive)

    if not json_files:
        raise ValueError(f"No JSON files found in {input_path}")

    rows: list[dict[str, Any]] = []

    for json_file in json_files:
        with json_file.open("r", encoding="utf-8") as file:
            parsed_json = json.load(file)

        rows.extend(json_to_rows(parsed_json))

    formatted_rows = [format_result_row(row) for row in rows]
    write_workbook(output_path, [Sheet(RESULT_SHEET_NAME, RESULT_COLUMNS, formatted_rows)])
    print(f"Wrote {output_path} with 1 sheet and {len(rows)} row(s) from {len(json_files)} JSON file(s).")
    return 0


def default_output_path(input_path: Path) -> Path:
    if input_path.suffix.lower() == ".json":
        return input_path.with_suffix(".xlsx")

    return input_path.with_suffix(".xlsx") if input_path.suffix else input_path.parent / f"{input_path.name}.xlsx"


def collect_json_files(input_path: Path, recursive: bool) -> list[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() != ".json":
            raise ValueError(f"Input file is not a JSON file: {input_path}")

        return [input_path]

    pattern = "**/*.json" if recursive else "*.json"
    return sorted(path for path in input_path.glob(pattern) if path.is_file())


def json_to_rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return array_to_rows(value)

    if isinstance(value, dict):
        entries = list(value.items())
        array_entries = [(key, item) for key, item in entries if isinstance(item, list)]

        if entries and len(entries) == len(array_entries):
            rows: list[dict[str, Any]] = []

            for _key, item in array_entries:
                rows.extend(array_to_rows(item))

            return rows

        row = flatten_record(value)
        return [row if row else {"value": "{}"}]

    return [{"value": value}]


def array_to_rows(values: list[Any]) -> list[dict[str, Any]]:
    if not values:
        return []

    rows: list[dict[str, Any]] = []

    for value in values:
        if isinstance(value, dict):
            rows.append(flatten_record(value))
        else:
            rows.append({"value": normalize_cell_value(value)})

    return rows


def format_result_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "run": row.get("run"),
        "framework": row.get("framework"),
        "browser": row.get("browser"),
        "action": row.get("action"),
        "zeit": parse_time_ms(
            first_existing(row, ["zeit", "performance", "time", "duration", "duration_ms"]),
        ),
    }


def first_existing(row: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in row:
            return row[key]

    return None


def parse_time_ms(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value

    text = str(value).strip()
    match = re.fullmatch(r"(-?\d+(?:[.,]\d+)?)\s*ms", text, flags=re.IGNORECASE)

    if match:
        return float(match.group(1).replace(",", "."))

    return value


def flatten_record(value: Any, prefix: str = "", row: dict[str, Any] | None = None) -> dict[str, Any]:
    if row is None:
        row = {}

    if isinstance(value, dict):
        if not value and prefix:
            row[prefix] = "{}"
            return row

        for key, entry_value in value.items():
            nested_key = f"{prefix}.{key}" if prefix else str(key)
            flatten_record(entry_value, nested_key, row)

        return row

    row[prefix or "value"] = normalize_cell_value(value)
    return row


def normalize_cell_value(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    return value


def write_workbook(output_path: Path, raw_sheets: list[Sheet]) -> None:
    if not raw_sheets:
        raise ValueError("Cannot create an Excel workbook without sheets.")

    sheets = prepare_sheets(raw_sheets)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(output_path, "w", compression=ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", content_types_xml(sheets))
        workbook.writestr("_rels/.rels", root_relationships_xml())
        workbook.writestr("docProps/app.xml", app_properties_xml(len(sheets)))
        workbook.writestr("docProps/core.xml", core_properties_xml())
        workbook.writestr("xl/workbook.xml", workbook_xml(sheets))
        workbook.writestr("xl/_rels/workbook.xml.rels", workbook_relationships_xml(sheets))
        workbook.writestr("xl/styles.xml", styles_xml())

        for sheet in sheets:
            workbook.writestr(f"xl/worksheets/sheet{sheet.sheet_id}.xml", worksheet_xml(sheet))
            workbook.writestr(
                f"xl/worksheets/_rels/sheet{sheet.sheet_id}.xml.rels",
                worksheet_relationships_xml(sheet),
            )
            workbook.writestr(f"xl/tables/table{sheet.sheet_id}.xml", table_xml(sheet))


def prepare_sheets(raw_sheets: list[Sheet]) -> list[Sheet]:
    used_names: set[str] = set()
    sheets: list[Sheet] = []

    for index, sheet in enumerate(raw_sheets, start=1):
        columns = sheet.columns or ["value"]
        row_count = len(sheet.rows) + 1

        if row_count > MAX_EXCEL_ROWS:
            raise ValueError(
                f'Sheet "{sheet.name}" has {row_count} rows, but Excel supports {MAX_EXCEL_ROWS}.',
            )

        if len(columns) > MAX_EXCEL_COLUMNS:
            raise ValueError(
                f'Sheet "{sheet.name}" has {len(columns)} columns, but Excel supports {MAX_EXCEL_COLUMNS}.',
            )

        prepared_sheet = Sheet(
            name=unique_sheet_name(sheet.name, used_names),
            columns=columns,
            rows=sheet.rows,
            sheet_id=index,
            table_name=f"Table{index}",
            headers=unique_headers(columns),
            ref=f"A1:{column_name(len(columns))}{max(row_count, 1)}",
        )
        sheets.append(prepared_sheet)

    return sheets


def unique_sheet_name(raw_name: str, used_names: set[str]) -> str:
    sanitized = re.sub(r"[\[\]:*?/\\]", " ", str(raw_name or "Sheet"))
    sanitized = re.sub(r"\s+", " ", sanitized).strip() or "Sheet"
    base_name = truncate_sheet_name(sanitized)
    name = base_name
    counter = 2

    while name.lower() in used_names:
        suffix = f" {counter}"
        name = f"{truncate_sheet_name(base_name, len(suffix))}{suffix}"
        counter += 1

    used_names.add(name.lower())
    return name


def truncate_sheet_name(name: str, reserved_length: int = 0) -> str:
    return name[: 31 - reserved_length].strip() or "Sheet"


def unique_headers(columns: list[str]) -> list[str]:
    used_headers: dict[str, int] = {}
    headers: list[str] = []

    for index, column in enumerate(columns, start=1):
        raw_header = str(column or f"Column {index}").strip() or f"Column {index}"
        base_header = truncate_text(raw_header, MAX_HEADER_TEXT_LENGTH)
        lower_header = base_header.lower()
        count = used_headers.get(lower_header, 0)
        used_headers[lower_header] = count + 1

        if count == 0:
            headers.append(base_header)
            continue

        suffix = f"_{count + 1}"
        headers.append(f"{base_header[: MAX_HEADER_TEXT_LENGTH - len(suffix)]}{suffix}")

    return headers


def content_types_xml(sheets: list[Sheet]) -> str:
    sheet_overrides = "".join(
        f'<Override PartName="/xl/worksheets/sheet{sheet.sheet_id}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for sheet in sheets
    )
    table_overrides = "".join(
        f'<Override PartName="/xl/tables/table{sheet.sheet_id}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.table+xml"/>'
        for sheet in sheets
    )

    return xml(
        f"""<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
  {sheet_overrides}
  {table_overrides}
</Types>""",
    )


def root_relationships_xml() -> str:
    return xml(
        f"""<Relationships xmlns="{PACKAGE_REL_NS}">
  <Relationship Id="rId1" Type="{REL_NS}/officeDocument" Target="xl/workbook.xml"/>
  <Relationship Id="rId2" Type="{PACKAGE_REL_NS}/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="{REL_NS}/extended-properties" Target="docProps/app.xml"/>
</Relationships>""",
    )


def app_properties_xml(sheet_count: int) -> str:
    return xml(
        f"""<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>json-to-excel.py</Application>
  <DocSecurity>0</DocSecurity>
  <ScaleCrop>false</ScaleCrop>
  <HeadingPairs>
    <vt:vector size="2" baseType="variant">
      <vt:variant><vt:lpstr>Worksheets</vt:lpstr></vt:variant>
      <vt:variant><vt:i4>{sheet_count}</vt:i4></vt:variant>
    </vt:vector>
  </HeadingPairs>
  <TitlesOfParts>
    <vt:vector size="0" baseType="lpstr"/>
  </TitlesOfParts>
  <Company/>
  <LinksUpToDate>false</LinksUpToDate>
  <SharedDoc>false</SharedDoc>
  <HyperlinksChanged>false</HyperlinksChanged>
  <AppVersion>1.0</AppVersion>
</Properties>""",
    )


def core_properties_xml() -> str:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    return xml(
        f"""<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>json-to-excel.py</dc:creator>
  <cp:lastModifiedBy>json-to-excel.py</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>
</cp:coreProperties>""",
    )


def workbook_xml(sheets: list[Sheet]) -> str:
    sheet_entries = "".join(
        f'<sheet name={quote_attr(sheet.name)} sheetId="{sheet.sheet_id}" r:id="rId{sheet.sheet_id}"/>'
        for sheet in sheets
    )

    return xml(
        f"""<workbook xmlns="{XLSX_NS}" xmlns:r="{REL_NS}">
  <sheets>{sheet_entries}</sheets>
</workbook>""",
    )


def workbook_relationships_xml(sheets: list[Sheet]) -> str:
    sheet_relationships = "".join(
        f'<Relationship Id="rId{sheet.sheet_id}" Type="{REL_NS}/worksheet" '
        f'Target="worksheets/sheet{sheet.sheet_id}.xml"/>'
        for sheet in sheets
    )
    styles_rel_id = len(sheets) + 1

    return xml(
        f"""<Relationships xmlns="{PACKAGE_REL_NS}">
  {sheet_relationships}
  <Relationship Id="rId{styles_rel_id}" Type="{REL_NS}/styles" Target="styles.xml"/>
</Relationships>""",
    )


def styles_xml() -> str:
    return xml(
        f"""<styleSheet xmlns="{XLSX_NS}">
  <fonts count="1"><font><sz val="11"/><color theme="1"/><name val="Calibri"/><family val="2"/><scheme val="minor"/></font></fonts>
  <fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
  <borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
  <cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
  <cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
  <dxfs count="0"/>
  <tableStyles count="1" defaultTableStyle="TableStyleMedium2" defaultPivotStyle="PivotStyleLight16"/>
</styleSheet>""",
    )


def worksheet_xml(sheet: Sheet) -> str:
    headers = sheet.headers or sheet.columns
    rows = [
        row_xml(1, headers),
        *(
            row_xml(row_index + 2, [row.get(column) for column in sheet.columns])
            for row_index, row in enumerate(sheet.rows)
        ),
    ]

    return xml(
        f"""<worksheet xmlns="{XLSX_NS}" xmlns:r="{REL_NS}">
  <dimension ref="{sheet.ref}"/>
  <sheetViews><sheetView workbookViewId="0"/></sheetViews>
  <sheetFormatPr defaultRowHeight="15"/>
  {column_widths_xml(sheet)}
  <sheetData>{''.join(rows)}</sheetData>
  <tableParts count="1"><tablePart r:id="rId1"/></tableParts>
</worksheet>""",
    )


def worksheet_relationships_xml(sheet: Sheet) -> str:
    return xml(
        f"""<Relationships xmlns="{PACKAGE_REL_NS}">
  <Relationship Id="rId1" Type="{REL_NS}/table" Target="../tables/table{sheet.sheet_id}.xml"/>
</Relationships>""",
    )


def table_xml(sheet: Sheet) -> str:
    headers = sheet.headers or sheet.columns
    table_columns = "".join(
        f'<tableColumn id="{index}" name={quote_attr(header)}/>'
        for index, header in enumerate(headers, start=1)
    )

    return xml(
        f"""<table xmlns="{XLSX_NS}" id="{sheet.sheet_id}" name="{sheet.table_name}" displayName="{sheet.table_name}" ref="{sheet.ref}" totalsRowShown="0">
  <autoFilter ref="{sheet.ref}"/>
  <tableColumns count="{len(headers)}">{table_columns}</tableColumns>
  <tableStyleInfo name="TableStyleMedium2" showFirstColumn="0" showLastColumn="0" showRowStripes="1" showColumnStripes="0"/>
</table>""",
    )


def row_xml(row_number: int, values: list[Any]) -> str:
    cells = "".join(
        cell_xml(f"{column_name(index)}{row_number}", value)
        for index, value in enumerate(values, start=1)
    )

    return f'<row r="{row_number}">{cells}</row>'


def cell_xml(reference: str, value: Any) -> str:
    if value is None:
        return f'<c r="{reference}"/>'

    if isinstance(value, bool):
        return f'<c r="{reference}" t="b"><v>{1 if value else 0}</v></c>'

    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        return f'<c r="{reference}"><v>{value}</v></c>'

    text = truncate_text(str(value), MAX_CELL_TEXT_LENGTH)
    return f'<c r="{reference}" t="inlineStr"><is><t xml:space="preserve">{escape_text(text)}</t></is></c>'


def column_widths_xml(sheet: Sheet) -> str:
    headers = sheet.headers or sheet.columns
    columns = []

    for index, header in enumerate(headers, start=1):
        sample_values = [row.get(sheet.columns[index - 1]) for row in sheet.rows[:100]]
        max_length = max(len(str(value or "")) for value in [header, *sample_values])
        width = min(max(max_length + 2, 10), 60)
        columns.append(f'<col min="{index}" max="{index}" width="{width}" customWidth="1"/>')

    return f"<cols>{''.join(columns)}</cols>"


def column_name(index: int) -> str:
    name = ""
    dividend = index

    while dividend > 0:
        dividend, modulo = divmod(dividend - 1, 26)
        name = chr(65 + modulo) + name

    return name


def xml(content: str) -> str:
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n{content}'


def escape_text(value: str) -> str:
    return escape(clean_xml_string(value))


def quote_attr(value: str) -> str:
    return quoteattr(clean_xml_string(value))


def clean_xml_string(value: str) -> str:
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)


def truncate_text(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value

    return f"{value[: max_length - 3]}..."


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
