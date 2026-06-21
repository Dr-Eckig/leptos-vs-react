use leptos::prelude::*;

use crate::types::{serialize::{AllBoards, BoardId, ColumnType, TaskId}, state::{BoardState, TaskState}};

#[derive(Clone, Copy, Debug)]
pub struct AllBoardsState {
    pub boards: RwSignal<Vec<BoardState>>,
    pub current_board_id: RwSignal<Option<BoardId>>,
}

impl AllBoardsState {
    pub fn from_all_boards(all_boards: AllBoards) -> Self {
        all_boards.into()
    }

    pub fn current_board(&self) -> Option<BoardState> {
        self.boards.with(|boards| {
            boards
                .iter()
                .find(|board| Some(board.id) == self.current_board_id.get())
                .copied()
        })
    }

    pub fn set_current_board(&self, board_id: BoardId) {
        self.current_board_id.set(Some(board_id));
    }

    pub fn add_board(&self, board: BoardState) {
        self.boards.update(|boards| boards.push(board));
        self.set_current_board(board.id);
    }

    pub fn add_task_to_current_board(&self, column_type: &ColumnType, task: TaskState) {
        if let Some(board) = self.current_board() {
            board.add_task_to_column(column_type, task);
        }
    }

    pub fn delete_task_from_current_board(&self, task_id: &TaskId) {
        if let Some(board) = self.current_board() {
            board.delete_task(task_id);
        }
    }

    pub fn move_task_in_current_board(
        &self,
        task_id: &TaskId,
        to_column_type: &ColumnType,
        before_task_id: Option<TaskId>,
    ) -> bool {
        self.current_board()
            .map(|board| board.move_task(task_id, to_column_type, before_task_id))
            .unwrap_or(false)
    }
}

impl From<AllBoards> for AllBoardsState {
    fn from(all_boards: AllBoards) -> Self {
        let serialized_current_board_id = all_boards.current_board_id();
        let board_states: Vec<BoardState> =
            all_boards.boards().iter().map(BoardState::from).collect();

        let current_board_id = serialized_current_board_id
            .filter(|current_id| board_states.iter().any(|board| board.id == *current_id))
            .or_else(|| board_states.first().map(|board| board.id));

        Self {
            boards: RwSignal::new(board_states),
            current_board_id: RwSignal::new(current_board_id),
        }
    }
}