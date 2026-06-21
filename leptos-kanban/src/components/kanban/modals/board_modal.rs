use leptos::prelude::*;

use crate::{
    components::{Input, Modal},
    performance::{self, PerformanceAction, PerformanceContext},
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
    let close_modal_without_measurement = move || app.modals.board.set(None);
    let close_modal = move || {
        if !is_open.get_untracked() {
            app.modals.board.set(None);
            return;
        }

        let measurement = performance::start(
            PerformanceAction::ModalClose,
            PerformanceContext::from_board(app.boards.current_board()),
        );
        app.modals.board.set(None);
        (measurement)();
    };

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
                let measurement = match board.get() {
                    Some(board_state) => {
                        let measurement = performance::start(
                            PerformanceAction::BoardEdit,
                            PerformanceContext::from_board(app.boards.current_board()),
                        );
                        board_state.title.set(new_board.title().to_string());
                        measurement
                    }
                    None => {
                        let board_state = BoardState::from_board(&new_board);
                        let measurement = performance::start(
                            PerformanceAction::BoardCreate,
                            PerformanceContext::from_board(app.boards.current_board()),
                        );
                        app.boards.add_board(board_state);
                        measurement
                    }
                };

                close_modal_without_measurement();
                (measurement)();
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
