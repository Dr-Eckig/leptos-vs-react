use leptos::prelude::*;

use crate::types::{state::ColumnState, validation::column::UserColumn};

#[derive(Clone)]
pub struct OpenColumnModal {
    pub column: ColumnState,
}

impl OpenColumnModal {
    pub fn new_with_column(column: ColumnState) -> Self {
        Self { column }
    }
}

#[derive(Clone, Copy)]
pub struct ColumnFormState {
    pub wip_limit: RwSignal<String>,
    pub limit_error: RwSignal<Option<String>>,
}

impl ColumnFormState {
    pub fn new(column: ColumnState) -> Self {
        Self {
            wip_limit: RwSignal::new(
                column
                    .wip_limit
                    .get_untracked()
                    .map(|limit| limit.to_string())
                    .unwrap_or_default(),
            ),
            limit_error: RwSignal::new(None),
        }
    }

    pub fn user_column(self, column: ColumnState) -> UserColumn {
        UserColumn {
            column_type: column.column_type,
            wip_limit: self.wip_limit.get_untracked(),
        }
    }

    pub fn clear_error(self) {
        self.limit_error.set(None);
    }

    pub fn set_validation_error(self) {
        self.limit_error
            .set(Some(String::from("Please enter a valid number.")));
    }
}
