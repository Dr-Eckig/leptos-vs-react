use std::cell::{Cell, RefCell};
use std::rc::Rc;
use std::sync::atomic::{AtomicUsize, Ordering};

use leptos::{
    leptos_dom::{helpers::request_animation_frame, logging::console_log},
    prelude::GetUntracked,
};
use serde::Serialize;
use wasm_bindgen::{JsCast, JsValue, closure::Closure};
use web_sys::js_sys;

use crate::types::state::BoardState;

const LOG_PREFIX: &str = "[leptos-kanban-performance]";

static NEXT_MEASUREMENT_ID: AtomicUsize = AtomicUsize::new(1);

thread_local! {
    static PERFORMANCE_LOG_FILE_NAME: RefCell<Option<String>> = const { RefCell::new(None) };
    static PERFORMANCE_LOG_ENTRIES: RefCell<Vec<PerformanceLogEntry>> = const { RefCell::new(Vec::new()) };
}

#[derive(Clone, Copy, Debug)]
pub enum PerformanceAction {
    BoardSwitch,
    TaskCreate,
    TaskEdit,
    TaskDelete,
    TaskMoveWithinColumn,
    TaskMoveBetweenColumns,
}

impl PerformanceAction {
    fn as_str(self) -> &'static str {
        match self {
            Self::BoardSwitch => "board-switch",
            Self::TaskCreate => "task-create",
            Self::TaskEdit => "task-edit",
            Self::TaskDelete => "task-delete",
            Self::TaskMoveWithinColumn => "task-move-within-column",
            Self::TaskMoveBetweenColumns => "task-move-between-columns",
        }
    }
}

#[derive(Clone, Debug)]
pub struct PerformanceContext {
    pub board_title: String,
}

#[derive(Clone, Debug, Serialize)]
struct PerformanceLogEntry {
    id: String,
    framework: String,
    board: String,
    action: String,
    performance: String,
    #[serde(rename = "domMutations")]
    dom_mutations: DomMutationSummary,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
struct DomMutationSummary {
    mutation_records: usize,
    text_changes: usize,
    attribute_changes: usize,
    added_elements: usize,
    removed_elements: usize,
}

impl PerformanceContext {
    pub fn from_board(board: Option<BoardState>) -> Self {
        let board_title = board
            .map(|board| board.title.get_untracked())
            .unwrap_or_else(|| String::from("no-board"));

        Self { board_title }
    }
}

pub type FinishPerformanceMeasurement = Box<dyn Fn()>;

pub fn start(
    action: PerformanceAction,
    context: PerformanceContext,
) -> FinishPerformanceMeasurement {
    let Some(window) = web_sys::window() else {
        return Box::new(|| {});
    };

    let Some(performance_api) = window.performance() else {
        return Box::new(|| {});
    };

    let id = NEXT_MEASUREMENT_ID.fetch_add(1, Ordering::Relaxed);
    let log_id = format!("{} {}", LOG_PREFIX, id);
    let board_title = sanitize_log_segment(&context.board_title);
    let action_name = action.as_str().to_string();

    let label = format!(
        "{} - {} - {}",
        id,
        sanitize_log_segment(&context.board_title),
        action.as_str(),
    );

    let start_mark = format!("leptos-kanban:{id}:start");
    let end_mark = format!("leptos-kanban:{id}:end");

    if performance_api.mark(&start_mark).is_err() {
        return Box::new(|| {});
    }

    let dom_mutation_measurement_id = start_dom_mutation_measurement();

    let is_finished = Rc::new(Cell::new(false));

    Box::new(move || {
        if is_finished.replace(true) {
            return;
        }

        let performance_api = performance_api.clone();
        let start_mark = start_mark.clone();
        let end_mark = end_mark.clone();
        let label = label.clone();

        let log_id = log_id.clone();
        let board_title = board_title.clone();
        let action_name = action_name.clone();
        let dom_mutation_measurement_id = dom_mutation_measurement_id.clone();

        after_next_paint(move || {
            let duration = measure_duration(&performance_api, &label, &start_mark, &end_mark);
            let dom_mutations = finish_dom_mutation_measurement(&dom_mutation_measurement_id);

            let Some(duration) = duration else {
                clear_performance_entries(&performance_api, &start_mark, &end_mark, &label);
                return;
            };

            let performance = format!("{:.2} ms", duration);

            console_log(&format!(
                "{} {} - {:.2} ms - {}",
                LOG_PREFIX,
                label,
                duration,
                dom_mutation_console_summary(&dom_mutations),
            ));

            append_performance_log(PerformanceLogEntry {
                id: log_id,
                framework: String::from("Leptos"),
                board: board_title,
                action: action_name,
                performance,
                dom_mutations,
            });

            clear_performance_entries(&performance_api, &start_mark, &end_mark, &label);
        });
    })
}

fn measure_duration(
    performance_api: &web_sys::Performance,
    label: &str,
    start_mark: &str,
    end_mark: &str,
) -> Option<f64> {
    performance_api.mark(end_mark).ok()?;
    performance_api
        .measure_with_start_mark_and_end_mark(label, start_mark, end_mark)
        .ok()?;

    let entries = performance_api.get_entries_by_name_with_entry_type(label, "measure");
    let last_index = entries.length().checked_sub(1)?;
    let entry = entries
        .get(last_index)
        .dyn_into::<web_sys::PerformanceEntry>()
        .ok()?;

    Some(entry.duration())
}

fn after_next_paint(callback: impl FnOnce() + 'static) {
    request_animation_frame(move || {
        let Ok(channel) = web_sys::MessageChannel::new() else {
            callback();
            return;
        };

        let on_message = Closure::once_into_js(callback);
        channel
            .port1()
            .set_onmessage(Some(on_message.unchecked_ref()));

        let _ = channel.port2().post_message(&JsValue::UNDEFINED);
    });
}

fn clear_performance_entries(
    performance_api: &web_sys::Performance,
    start_mark: &str,
    end_mark: &str,
    label: &str,
) {
    performance_api.clear_marks_with_mark_name(start_mark);
    performance_api.clear_marks_with_mark_name(end_mark);
    performance_api.clear_measures_with_measure_name(label);
}

fn sanitize_log_segment(value: &str) -> String {
    value.replace(['\n', '\r'], "_")
}

fn start_dom_mutation_measurement() -> JsValue {
    let Some(metrics) = dom_mutation_metrics() else {
        return JsValue::NULL;
    };

    let Ok(start) = js_sys::Reflect::get(&metrics, &JsValue::from_str("startMeasurement")) else {
        return JsValue::NULL;
    };

    let Ok(start) = start.dyn_into::<js_sys::Function>() else {
        return JsValue::NULL;
    };

    start.call0(&metrics).unwrap_or(JsValue::NULL)
}

fn finish_dom_mutation_measurement(measurement_id: &JsValue) -> DomMutationSummary {
    let Some(metrics) = dom_mutation_metrics() else {
        return empty_dom_mutation_summary();
    };

    let Ok(finish) = js_sys::Reflect::get(&metrics, &JsValue::from_str("finishMeasurement")) else {
        return empty_dom_mutation_summary();
    };

    let Ok(finish) = finish.dyn_into::<js_sys::Function>() else {
        return empty_dom_mutation_summary();
    };

    let Ok(summary) = finish.call1(&metrics, measurement_id) else {
        return empty_dom_mutation_summary();
    };

    DomMutationSummary {
        mutation_records: js_property_usize(&summary, "mutationRecords").unwrap_or(0),
        text_changes: js_property_usize(&summary, "textChanges").unwrap_or(0),
        attribute_changes: js_property_usize(&summary, "attributeChanges").unwrap_or(0),
        added_elements: js_property_usize(&summary, "addedElements").unwrap_or(0),
        removed_elements: js_property_usize(&summary, "removedElements").unwrap_or(0),
    }
}

fn dom_mutation_metrics() -> Option<JsValue> {
    let window = web_sys::window()?;

    js_sys::Reflect::get(&window, &JsValue::from_str("KanbanDomMutationMetrics"))
        .ok()
        .filter(|value| !value.is_null() && !value.is_undefined())
}

fn js_property_usize(value: &JsValue, property: &str) -> Option<usize> {
    js_sys::Reflect::get(value, &JsValue::from_str(property))
        .ok()
        .and_then(|value| value.as_f64())
        .map(|value| value as usize)
}

fn empty_dom_mutation_summary() -> DomMutationSummary {
    DomMutationSummary {
        mutation_records: 0,
        text_changes: 0,
        attribute_changes: 0,
        added_elements: 0,
        removed_elements: 0,
    }
}

fn dom_mutation_console_summary(dom_mutations: &DomMutationSummary) -> String {
    format!(
        "dom: records={} text={} attributes={} added={} removed={}",
        dom_mutations.mutation_records,
        dom_mutations.text_changes,
        dom_mutations.attribute_changes,
        dom_mutations.added_elements,
        dom_mutations.removed_elements,
    )
}

pub fn init_performance_log_session() {
    PERFORMANCE_LOG_FILE_NAME.with(|file_name| {
        *file_name.borrow_mut() = Some(create_performance_log_file_name());
    });

    PERFORMANCE_LOG_ENTRIES.with(|entries| {
        entries.borrow_mut().clear();
    });
}

fn create_performance_log_file_name() -> String {
    let date = js_sys::Date::new_0();

    format!(
        "leptos - {:04}-{:02}-{:02} - {:02}.{:02}.{:02}.json",
        date.get_full_year(),
        date.get_month() + 1,
        date.get_date(),
        date.get_hours(),
        date.get_minutes(),
        date.get_seconds(),
    )
}

fn append_performance_log(entry: PerformanceLogEntry) {
    PERFORMANCE_LOG_ENTRIES.with(|entries| {
        entries.borrow_mut().push(entry);
    });
}

pub fn performance_log_file_content() -> String {
    PERFORMANCE_LOG_ENTRIES.with(|entries| {
        serde_json::to_string_pretty(&*entries.borrow()).unwrap_or_else(|_| String::from("[]"))
    })
}

pub fn performance_log_file_name() -> String {
    PERFORMANCE_LOG_FILE_NAME.with(|file_name| {
        file_name
            .borrow()
            .clone()
            .unwrap_or_else(create_performance_log_file_name)
    })
}
