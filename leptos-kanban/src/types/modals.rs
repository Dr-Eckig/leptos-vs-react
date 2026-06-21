use crate::types::{serialize::ColumnType, state::{BoardState, ColumnState, TaskState}};


#[derive(Clone)]
pub struct OpenTaskModal {
    pub column_id: Option<ColumnType>,
    pub task: Option<TaskState>,
}

impl OpenTaskModal {
    pub fn new(column_id: Option<ColumnType>) -> Self {
        Self { column_id, task: None }
    }

    pub fn new_with_task(column_id: ColumnType, task: TaskState) -> Self {
        Self { column_id: Some(column_id), task: Some(task) }
    }
}

#[derive(Clone)]
pub struct OpenColumnModal {
    pub column: ColumnState,
}

impl OpenColumnModal {
    pub fn new_with_column(column: ColumnState) -> Self {
        Self { column }
    }
}

#[derive(Clone)]
pub struct OpenBoardModal {
    pub board: Option<BoardState>,
}

impl OpenBoardModal {
    pub fn new() -> Self {
        Self { board: None }
    }

    pub fn new_with_board(board: BoardState) -> Self {
        Self { board: Some(board) }
    }
}
