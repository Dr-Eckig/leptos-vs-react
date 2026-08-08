use leptos::prelude::GetUntracked;
use wasm_bindgen::{JsCast, JsValue};
use web_sys::js_sys;

use crate::types::state::BoardState;

const GLOBAL_NAME: &str = "KanbanPerformanceMetrics";

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
    let measurement_id = call_shared(
        "startMeasurement",
        &[
            JsValue::from_str(&context.board_title),
            JsValue::from_str(action.as_str()),
        ],
    )
    .unwrap_or(JsValue::NULL);

    Box::new(move || {
        let _ = call_shared("finishMeasurement", &[measurement_id.clone()]);
    })
}

pub fn init_performance_log_session() {
    let _ = call_shared(
        "initSession",
        &[JsValue::from_str("Leptos"), JsValue::from_str("leptos")],
    );
}

pub fn performance_log_file_content() -> String {
    call_shared("logFileContent", &[])
        .and_then(|value| value.as_string())
        .unwrap_or_else(|| String::from("[]"))
}

pub fn performance_log_file_name() -> String {
    call_shared("logFileName", &[])
        .and_then(|value| value.as_string())
        .unwrap_or_else(|| String::from("leptos-performance.json"))
}

fn call_shared(method_name: &str, arguments: &[JsValue]) -> Option<JsValue> {
    let window = web_sys::window()?;
    let metrics = js_sys::Reflect::get(&window, &JsValue::from_str(GLOBAL_NAME)).ok()?;
    let method = js_sys::Reflect::get(&metrics, &JsValue::from_str(method_name)).ok()?;
    let method = method.dyn_into::<js_sys::Function>().ok()?;
    let arguments = js_sys::Array::from_iter(arguments.iter());

    method.apply(&metrics, &arguments).ok()
}
