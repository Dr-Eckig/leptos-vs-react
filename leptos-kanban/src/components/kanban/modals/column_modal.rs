use leptos::prelude::*;

use crate::{
    components::{Input, Modal},
    types::{
        app_context::AppContext, modals::OpenColumnModal, state::ColumnState, ui::InputType,
        validation::column::UserColumn,
    },
};

#[derive(Clone, Copy)]
struct ColumnFormState {
    wip_limit: RwSignal<String>,
    limit_error: RwSignal<Option<String>>,
}

impl ColumnFormState {
    fn new(column: ColumnState) -> Self {
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

    fn user_column(self, column: ColumnState) -> UserColumn {
        UserColumn {
            column_type: column.column_type,
            wip_limit: self.wip_limit.get_untracked(),
        }
    }

    fn clear_error(self) {
        self.limit_error.set(None);
    }

    fn set_validation_error(self) {
        self.limit_error
            .set(Some(String::from("Please enter a valid number.")));
    }
}

#[component]
pub fn ColumnModal() -> impl IntoView {
    let app: AppContext = expect_context();

    view! {
        {move || {
            app.modals
                .column
                .get()
                .map(|data| view! { <ColumnModalContent data /> })
        }}
    }
}

#[component]
fn ColumnModalContent(data: OpenColumnModal) -> impl IntoView {
    let app: AppContext = expect_context();
    let column = data.column;
    let form = ColumnFormState::new(column);

    let close_modal = move || app.modals.column.set(None);
    let save_column = move || {
        form.clear_error();

        match form.user_column(column).validate() {
            Ok(validated_column) => {
                update_column(column, *validated_column.wip_limit());
                close_modal();
            }
            Err(_) => form.set_validation_error(),
        }
    };

    view! {
        <Modal
            title=format!("Edit Column: {}", column.column_type.display_name())
            is_open=Signal::derive(move || true)
            on_save=save_column
            close=close_modal
        >
            <ColumnFormFields form />
        </Modal>
    }
}

#[component]
fn ColumnFormFields(form: ColumnFormState) -> impl IntoView {
    view! {
        <Input
            label="WIP Limit"
            value=form.wip_limit
            input_type=InputType::Number
            error_message=Signal::derive(move || form.limit_error.get())
            min=0
        />
    }
}

fn update_column(column: ColumnState, wip_limit: Option<u32>) {
    column.wip_limit.set(wip_limit);
}
