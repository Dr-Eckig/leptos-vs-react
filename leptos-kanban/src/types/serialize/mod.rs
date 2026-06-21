use serde::{Deserialize, Serialize};

mod board;
mod column;
mod task;

pub use board::{Board, BoardId};
pub use column::{Column, ColumnId, ColumnType};
pub use task::{Task, TaskId, Priority};

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct AllBoards {
    boards: Vec<Board>,
    current_board_id: Option<BoardId>,
}

impl AllBoards {
    pub fn boards(&self) -> &Vec<Board> {
        &self.boards
    }

    pub fn current_board_id(&self) -> Option<BoardId> {
        self.current_board_id
    }
}
