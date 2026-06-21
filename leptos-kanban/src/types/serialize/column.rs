use std::fmt;

use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::types::serialize::task::Task;

pub type ColumnId = Uuid;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Column {
    #[serde(default = "Uuid::new_v4")]
    id: ColumnId,
    column_type: ColumnType,
    #[serde(default = "Vec::new")]
    tasks: Vec<Task>,
    wip_limit: Option<u32>,
}

#[derive(Clone, Debug, PartialEq, Eq, Hash, Serialize, Deserialize, Copy)]
pub enum ColumnType {
    #[serde(rename = "todo")]
    Todo,
    #[serde(rename = "in_progress")]
    InProgress,
    #[serde(rename = "done")]
    Done,
}

impl Column {
    pub fn new(column_type: ColumnType, wip_limit: Option<u32>) -> Self {
        Self {
            id: Uuid::new_v4(),
            column_type,
            tasks: Vec::new(),
            wip_limit,
        }
    }

    pub fn id(&self) -> ColumnId {
        self.id
    }

    pub fn column_type(&self) -> ColumnType {
        self.column_type
    }

    pub fn tasks(&self) -> &Vec<Task> {
        &self.tasks
    }

    pub fn wip_limit(&self) -> &Option<u32> {
        &self.wip_limit
    }
}

impl ColumnType {
    pub fn display_name(&self) -> &'static str {
        match self {
            ColumnType::Todo => "To Do",
            ColumnType::InProgress => "In Progress",
            ColumnType::Done => "Done",
        }
    }

    pub fn name(&self) -> &'static str {
        match self {
            ColumnType::Todo => "todo",
            ColumnType::InProgress => "in_progress",
            ColumnType::Done => "done",
        }
    }

    pub fn all() -> [ColumnType; 3] {
        [
            ColumnType::Todo,
            ColumnType::InProgress,
            ColumnType::Done,
        ]
    }
}

impl fmt::Display for ColumnType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.display_name())
    }
}