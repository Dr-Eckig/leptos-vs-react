use leptos::prelude::*;

use crate::{
    components::{Input, Modal},
    types::{
        app_context::AppContext,
        state::BoardState,
        validation::board::{BoardValidationError, UserBoard},
    },
};

#[component]
pub fn BoardModal() -> impl IntoView {
    let app: AppContext = expect_context();

    let board = Signal::derive(move || app.modals.board.get().and_then(|modal| modal.board));
    let is_open = Signal::derive(move || app.modals.board.get().is_some());
    let close_modal = move || app.modals.board.set(None);

    let board_title = RwSignal::new(String::new());
    let title_error: RwSignal<Option<String>> = RwSignal::new(None::<String>);

    let is_edit = move || board.get().is_some();
    let modal_title = Signal::derive(move || {
        if is_edit() {
            "Edit Board".to_string()
        } else {
            "Add Board".to_string()
        }
    });

    Effect::new(move || {
        if is_open.get() {
            title_error.set(None);
        }
    });

    Effect::new(move || {
        if let Some(board_state) = board.get() {
            board_title.set(board_state.title.get());
        } else {
            board_title.set(String::new());
        }
    });

    let save_board = move || {
        let user_board = UserBoard {
            title: board_title.get(),
        };

        match user_board.validate() {
            Ok(new_board) => {
                match board.get() {
                    Some(board_state) => {
                        board_state.title.set(new_board.title().to_string());
                    }
                    None => {
                        let board_state = BoardState::from_board(&new_board);
                        app.boards.add_board(board_state);
                    }
                };

                close_modal();
            }
            Err(BoardValidationError::EmptyTitle) => {
                title_error.set(Some(String::from("The title must not be empty")));
            }
            Err(BoardValidationError::TitleTooLong) => {
                title_error.set(Some(String::from(
                    "Please enter a title with at most 200 characters.",
                )));
            }
        }
    };

    view! {
        <Modal title=modal_title is_open on_save=save_board close=close_modal>
            <Input
                label="Title"
                value=board_title
                error_message=Signal::derive(move || title_error.get())
            />
        </Modal>
    }
}
