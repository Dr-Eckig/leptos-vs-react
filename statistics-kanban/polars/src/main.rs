// cargo run --manifest-path statistics-kanban/polars/Cargo.toml -- playwright-kanban/results statistics-kanban/polars/performance-summary.json

use polars::prelude::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{
    env,
    error::Error,
    fs::{self, File},
    io::{self, BufWriter, Write},
    path::{Path, PathBuf},
};

#[derive(Debug, Deserialize)]
struct Measurement {
    #[serde(default)]
    framework: String,
    #[serde(default)]
    browser: String,
    #[serde(default)]
    action: String,
    #[serde(default)]
    board: String,
    performance: Value,
}

#[derive(Debug, Serialize)]
struct Summary {
    framework: String,
    browser: String,
    action: String,
    board: String,
    min: f64,
    max: f64,
    mean: f64,
    median: f64,
    #[serde(rename = "standardDeviation")]
    standard_deviation: f64,
}

fn main() -> Result<(), Box<dyn Error>> {
    let args = env::args().skip(1).collect::<Vec<_>>();

    if !(1..=2).contains(&args.len()) || args.iter().any(|arg| arg == "--help" || arg == "-h") {
        print_usage();
        return Ok(());
    }

    let input_dir = absolute_path(PathBuf::from(&args[0]))?;
    let output_path = absolute_path(
        args.get(1)
            .map(PathBuf::from)
            .unwrap_or_else(|| PathBuf::from("performance-summary.json")),
    )?;

    if !input_dir.is_dir() {
        return Err(format!("Input must be a folder: {}", input_dir.display()).into());
    }

    let mut json_files = Vec::new();
    collect_json_files(&input_dir, &output_path, &mut json_files)?;
    json_files.sort();

    if json_files.is_empty() {
        return Err(format!("No JSON files found in {}", input_dir.display()).into());
    }

    let summaries = json_files
        .iter()
        .map(|json_file| summarize_file(json_file))
        .collect::<Result<Vec<_>, _>>()?;

    if let Some(parent) = output_path.parent() {
        fs::create_dir_all(parent)?;
    }

    let output = File::create(&output_path)?;
    let mut writer = BufWriter::new(output);
    serde_json::to_writer_pretty(&mut writer, &summaries)?;
    writeln!(writer)?;

    println!(
        "Wrote {} summaries from {} JSON file(s) to {}",
        summaries.len(),
        json_files.len(),
        output_path.display()
    );

    Ok(())
}

fn print_usage() {
    println!(
        "Usage: cargo run -- <input-folder> [output-json]\n\n\
         Example:\n\
         cargo run -- ../../playwright-kanban/results performance-summary.json"
    );
}

fn absolute_path(path: PathBuf) -> io::Result<PathBuf> {
    if path.is_absolute() {
        Ok(path)
    } else {
        Ok(env::current_dir()?.join(path))
    }
}

fn collect_json_files(
    input_dir: &Path,
    output_path: &Path,
    json_files: &mut Vec<PathBuf>,
) -> io::Result<()> {
    for entry in fs::read_dir(input_dir)? {
        let path = entry?.path();

        if path.is_dir() {
            collect_json_files(&path, output_path, json_files)?;
        } else if is_json_file(&path) && path != output_path {
            json_files.push(path);
        }
    }

    Ok(())
}

fn is_json_file(path: &Path) -> bool {
    path.extension()
        .is_some_and(|extension| extension.eq_ignore_ascii_case("json"))
}

fn summarize_file(path: &Path) -> Result<Summary, Box<dyn Error>> {
    let input = File::open(path)?;
    let measurements = serde_json::from_reader::<_, Vec<Measurement>>(input)
        .map_err(|err| format!("Could not parse {}: {err}", path.display()))?;
    let first_measurement = measurements
        .first()
        .ok_or_else(|| format!("Cannot summarize empty file: {}", path.display()))?;
    let performance_ms = measurements
        .iter()
        .map(|measurement| parse_performance_ms(&measurement.performance, path))
        .collect::<Result<Vec<_>, _>>()?;

    let data_frame = df!("performance_ms" => performance_ms)?;
    let values = data_frame.column("performance_ms")?.f64()?;

    Ok(Summary {
        framework: first_measurement.framework.to_lowercase(),
        browser: first_measurement.browser.clone(),
        action: first_measurement.action.clone(),
        board: first_measurement.board.clone(),
        min: required_stat(values.min(), path, "min").map(round_to_two_decimals)?,
        max: required_stat(values.max(), path, "max").map(round_to_two_decimals)?,
        mean: required_stat(values.mean(), path, "mean").map(round_to_two_decimals)?,
        median: required_stat(values.median(), path, "median").map(round_to_two_decimals)?,
        standard_deviation: required_stat(values.std(1), path, "standard deviation")
            .map(round_to_two_decimals)?,
    })
}

fn round_to_two_decimals(value: f64) -> f64 {
    (value * 100.0).round() / 100.0
}

fn parse_performance_ms(value: &Value, path: &Path) -> Result<f64, Box<dyn Error>> {
    match value {
        Value::Number(number) => number
            .as_f64()
            .ok_or_else(|| format!("Invalid numeric performance in {}", path.display()).into()),
        Value::String(text) => {
            let normalized = text.trim().trim_end_matches("ms").trim().replace(',', ".");
            normalized.parse::<f64>().map_err(|err| {
                format!(
                    "Invalid performance value \"{text}\" in {}: {err}",
                    path.display()
                )
                .into()
            })
        }
        _ => Err(format!("Invalid performance value in {}", path.display()).into()),
    }
}

fn required_stat(
    value: Option<f64>,
    path: &Path,
    statistic_name: &str,
) -> Result<f64, Box<dyn Error>> {
    value.ok_or_else(|| {
        format!(
            "Could not calculate {statistic_name} for {}",
            path.display()
        )
        .into()
    })
}
