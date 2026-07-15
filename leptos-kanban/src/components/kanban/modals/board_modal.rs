use leptos::prelude::*;

use crate::{
    components::{Input, Modal},
    types::{
        app_context::AppContext,
        modals::OpenBoardModal,
        serialize::Board,
        state::BoardState,
        validation::board::{BoardValidationError, UserBoard},
    },
};

#[derive(Clone, Copy)]
struct BoardFormState {
    title: RwSignal<String>,
    title_error: RwSignal<Option<String>>,
}

impl BoardFormState {
    fn new(board: Option<BoardState>) -> Self {
        Self {
            title: RwSignal::new(
                board
                    .map(|board| board.title.get_untracked())
                    .unwrap_or_default(),
            ),
            title_error: RwSignal::new(None),
        }
    }

    fn user_board(self) -> UserBoard {
        UserBoard {
            title: self.title.get_untracked(),
        }
    }

    fn clear_error(self) {
        self.title_error.set(None);
    }

    fn set_validation_error(self, error: BoardValidationError) {
        let message = match error {
            BoardValidationError::EmptyTitle => "The title must not be empty",
            BoardValidationError::TitleTooLong => {
                "Please enter a title with at most 200 characters."
            }
        };

        self.title_error.set(Some(String::from(message)));
    }
}

#[component]
pub fn BoardModal() -> impl IntoView {
    let app: AppContext = expect_context();

    view! {
        {move || {
            app.modals
                .board
                .get()
                .map(|data| view! { <BoardModalContent data /> })
        }}
    }
}

#[component]
fn BoardModalContent(data: OpenBoardModal) -> impl IntoView {
    let app: AppContext = expect_context();
    let board = data.board;
    let form = BoardFormState::new(board);

    let close_modal = move || app.modals.board.set(None);
    let save_board = move || {
        form.clear_error();

        match form.user_board().validate() {
            Ok(validated_board) => {
                save_validated_board(app, board, validated_board);
                close_modal();
            }
            Err(error) => form.set_validation_error(error),
        }
    };

    let modal_title = if board.is_some() {
        "Edit Board"
    } else {
        "Add Board"
    };

    view! {
        <Modal
            title=modal_title
            is_open=Signal::derive(move || true)
            on_save=save_board
            close=close_modal
        >
            <BoardFormFields form />
        </Modal>
    }
}

#[component]
fn BoardFormFields(form: BoardFormState) -> impl IntoView {
    view! {
        <Input
            label="Title"
            value=form.title
            error_message=Signal::derive(move || form.title_error.get())
        />
    }
}

fn save_validated_board(app: AppContext, edited_board: Option<BoardState>, validated_board: Board) {
    if let Some(board_state) = edited_board {
        update_board(board_state, &validated_board);
    } else {
        app.boards
            .add_board(BoardState::from_board(&validated_board));
    }
}

fn update_board(board_state: BoardState, validated_board: &Board) {
    board_state.title.set(validated_board.title().to_string());
}
