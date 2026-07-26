use leptos::prelude::*;

use crate::{
    components::{Input, Modal},
    types::{app_context::AppContext, modals::BoardFormState, serialize::Board, state::BoardState},
};

#[component]
pub fn BoardModal() -> impl IntoView {
    let app: AppContext = expect_context();
    let form = BoardFormState::new(None);

    Effect::new(move || {
        if let Some(data) = app.modals.board.get() {
            form.set_board(data.board);
        }
    });

    let close_modal = move || {
        if app.modals.board.get_untracked().is_some() {
            app.modals.board.set(None);
        }
    };
    let save_board = move || {
        let Some(data) = app.modals.board.get_untracked() else {
            return;
        };

        form.clear_error();

        match form.user_board().validate() {
            Ok(validated_board) => {
                save_validated_board(app, data.board, validated_board);
                close_modal();
            }
            Err(error) => form.set_validation_error(error),
        }
    };

    let is_open = Signal::derive(move || app.modals.board.get().is_some());
    let modal_title = Signal::derive(move || {
        app.modals
            .board
            .get()
            .and_then(|data| data.board)
            .map(|_| String::from("Edit Board"))
            .unwrap_or_else(|| String::from("Add Board"))
    });

    view! {
        <Modal
            title=modal_title
            is_open
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
