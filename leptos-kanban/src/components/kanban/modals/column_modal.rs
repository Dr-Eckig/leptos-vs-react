use leptos::prelude::*;

use crate::{
    components::{Input, Modal},
    types::{
        app_context::AppContext,
        modals::{ColumnFormState, OpenColumnModal},
        state::ColumnState,
        ui::InputType,
    },
};

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
