use leptos::prelude::*;

use crate::{
    components::{Input, Modal},
    types::{app_context::AppContext, modals::ColumnFormState, state::ColumnState, ui::InputType},
};

#[component]
pub fn ColumnModal() -> impl IntoView {
    let app: AppContext = expect_context();
    let form = ColumnFormState::new(None);

    Effect::new(move || {
        if let Some(data) = app.modals.column.get() {
            form.set_column(Some(data.column));
        }
    });

    let close_modal = move || {
        if app.modals.column.get_untracked().is_some() {
            app.modals.column.set(None);
        }
    };
    let save_column = move || {
        let Some(data) = app.modals.column.get_untracked() else {
            return;
        };

        form.clear_error();

        match form.user_column(data.column).validate() {
            Ok(validated_column) => {
                update_column(data.column, *validated_column.wip_limit());
                close_modal();
            }
            Err(_) => form.set_validation_error(),
        }
    };

    let is_open = Signal::derive(move || app.modals.column.get().is_some());
    let modal_title = Signal::derive(move || {
        app.modals
            .column
            .get()
            .map(|data| format!("Edit Column: {}", data.column.column_type.display_name(),))
            .unwrap_or_else(|| String::from("Edit Column"))
    });

    view! {
        <Modal
            title=modal_title
            is_open
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
