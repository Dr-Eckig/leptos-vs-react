use leptos::prelude::*;

use crate::types::{
    drag_and_drop::DraggableItemDto,
    modals::{OpenBoardModal, OpenColumnModal, OpenTaskModal},
    state::AllBoardsState,
};

#[derive(Clone, Copy, Debug)]
pub struct ModalState {
    pub board: RwSignal<Option<OpenBoardModal>>,
    pub column: RwSignal<Option<OpenColumnModal>>,
    pub task: RwSignal<Option<OpenTaskModal>>,
}

impl ModalState {
    pub fn new() -> Self {
        Self {
            board: RwSignal::new(None),
            column: RwSignal::new(None),
            task: RwSignal::new(None),
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct DragAndDropState {
    pub dragged_item: RwSignal<Option<DraggableItemDto>>,
}

impl DragAndDropState {
    pub fn new() -> Self {
        Self {
            dragged_item: RwSignal::new(None),
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct AppContext {
    pub boards: AllBoardsState,
    pub modals: ModalState,
    pub drag_and_drop: DragAndDropState,
}

impl AppContext {
    pub fn new(boards: AllBoardsState) -> Self {
        Self {
            boards,
            modals: ModalState::new(),
            drag_and_drop: DragAndDropState::new(),
        }
    }
}
