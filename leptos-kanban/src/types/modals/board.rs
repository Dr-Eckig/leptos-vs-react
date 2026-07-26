use leptos::prelude::*;

use crate::types::{
    state::BoardState,
    validation::board::{BoardValidationError, UserBoard},
};

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

#[derive(Clone, Copy)]
pub struct BoardFormState {
    pub title: RwSignal<String>,
    pub title_error: RwSignal<Option<String>>,
}

impl BoardFormState {
    pub fn new(board: Option<BoardState>) -> Self {
        let form = Self {
            title: RwSignal::new(String::new()),
            title_error: RwSignal::new(None),
        };
        form.set_board(board);
        form
    }

    pub fn set_board(self, board: Option<BoardState>) {
        self.title.set(
            board
                .map(|board| board.title.get_untracked())
                .unwrap_or_default(),
        );
        self.clear_error();
    }

    pub fn user_board(self) -> UserBoard {
        UserBoard {
            title: self.title.get_untracked(),
        }
    }

    pub fn clear_error(self) {
        self.title_error.set(None);
    }

    pub fn set_validation_error(self, error: BoardValidationError) {
        let message = match error {
            BoardValidationError::EmptyTitle => "The title must not be empty",
            BoardValidationError::TitleTooLong => {
                "Please enter a title with at most 200 characters."
            }
        };

        self.title_error.set(Some(String::from(message)));
    }
}
