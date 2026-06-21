use leptos::{leptos_dom::logging::console_log, prelude::*};

use crate::{
    components::Board,
    types::{app_context::AppContext, serialize::AllBoards, state::AllBoardsState},
};

const MOCK_BOARD_JSON: &str = include_str!("../mock_data/mock_board.json");

#[component]
pub fn App() -> impl IntoView {
    let example_data = serde_json::from_str::<AllBoards>(MOCK_BOARD_JSON)
        .map_err(|err| console_log(&err.to_string()))
        .expect("Failed to parse mock board");

    let app_context = AppContext::new(AllBoardsState::from_all_boards(example_data));
    provide_context(app_context);

    view! { <Board /> }
}
