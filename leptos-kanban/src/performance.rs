use std::cell::{Cell, RefCell};
use std::rc::Rc;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Duration;

use leptos::{
    leptos_dom::{
        helpers::{request_animation_frame, set_timeout},
        logging::console_log,
    },
    prelude::GetUntracked,
};
use serde::Serialize;
use web_sys::js_sys;

use crate::types::state::BoardState;

const LOG_PREFIX: &str = "[leptos-kanban-performance]";

static NEXT_MEASUREMENT_ID: AtomicUsize = AtomicUsize::new(1);

thread_local! {
    static PERFORMANCE_LOG_FILE_NAME: RefCell<Option<String>> = RefCell::new(None);
    static PERFORMANCE_LOG_ENTRIES: RefCell<Vec<PerformanceLogEntry>> = RefCell::new(Vec::new());
}

#[derive(Clone, Copy, Debug)]
pub enum PerformanceAction {
    BoardCreate,
    BoardEdit,
    BoardSwitch,
    ColumnEdit,
    TaskCreate,
    TaskEdit,
    TaskDelete,
    TaskMoveWithinColumn,
    TaskMoveBetweenColumns,
    ModalOpen,
    ModalClose,
}

impl PerformanceAction {
    fn as_str(self) -> &'static str {
        match self {
            Self::BoardCreate => "board-create",
            Self::BoardEdit => "board-edit",
            Self::BoardSwitch => "board-switch",
            Self::ColumnEdit => "column-edit",
            Self::TaskCreate => "task-create",
            Self::TaskEdit => "task-edit",
            Self::TaskDelete => "task-delete",
            Self::TaskMoveWithinColumn => "task-move-within-column",
            Self::TaskMoveBetweenColumns => "task-move-between-columns",
            Self::ModalOpen => "modal-open",
            Self::ModalClose => "modal-close",
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

    let start_time = performance_api.now();

    if performance_api.mark(&start_mark).is_err() {
        return Box::new(|| {});
    }

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

        after_next_paint(move || {
            let _ = performance_api.mark(&end_mark);

            let duration = performance_api.now() - start_time;
            let performance = format!("{:.2} ms", duration);

            let _ = performance_api.measure_with_start_mark_and_end_mark(
                &label,
                &start_mark,
                &end_mark,
            );

            console_log(&format!("{} {} - {:.2} ms", LOG_PREFIX, label, duration));

            append_performance_log(PerformanceLogEntry {
                id: log_id,
                framework: String::from("Leptos"),
                board: board_title,
                action: action_name,
                performance,
            });

            clear_performance_entries(&performance_api, &start_mark, &end_mark, &label);
        });
    })
}

fn after_next_paint(callback: impl FnOnce() + 'static) {
    request_animation_frame(move || {
        set_timeout(callback, Duration::ZERO);
    });
}

fn clear_performance_entries(
    performance_api: &web_sys::Performance,
    start_mark: &str,
    end_mark: &str,
    label: &str,
) {
    let _ = performance_api.clear_marks_with_mark_name(start_mark);
    let _ = performance_api.clear_marks_with_mark_name(end_mark);
    let _ = performance_api.clear_measures_with_measure_name(label);
}

fn sanitize_log_segment(value: &str) -> String {
    value.replace('\n', "_").replace('\r', "_")
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
