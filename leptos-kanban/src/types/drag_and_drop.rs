use serde::{Deserialize, Serialize};

use crate::types::serialize::{ColumnType, TaskId};

pub const DRAGGABLE_ITEM_MIME_TYPE: &str = "application/x-leptos-kanban-task+json";
pub const DRAGGABLE_ITEM_TEXT_FALLBACK: &str = "text/plain";

#[derive(Clone, Copy, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DraggableItemDto {
    pub task_id: TaskId,
    pub source_column_type: ColumnType,
}

impl DraggableItemDto {
    pub fn new(task_id: TaskId, source_column_type: ColumnType) -> Self {
        Self {
            task_id,
            source_column_type,
        }
    }

    pub fn from_payload(payload: &str) -> Option<Self> {
        serde_json::from_str(payload).ok()
    }

    pub fn to_payload(self) -> Option<String> {
        serde_json::to_string(&self).ok()
    }
}
