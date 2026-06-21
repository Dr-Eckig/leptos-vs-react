use leptos::prelude::*;

use crate::{
    components::{Input, Modal},
    performance::{self, PerformanceAction, PerformanceContext},
    types::{
        app_context::AppContext,
        serialize::ColumnType,
        ui::InputType,
        validation::column::{ColumnValidationError, UserColumn},
    },
};

#[component]
pub fn ColumnModal() -> impl IntoView {
    let app: AppContext = expect_context();

    let column = Signal::derive(move || app.modals.column.get().map(|modal| modal.column));
    let is_open = Signal::derive(move || app.modals.column.get().is_some());
    let close_modal_without_measurement = move || app.modals.column.set(None);
    let close_modal = move || {
        if !is_open.get_untracked() {
            app.modals.column.set(None);
            return;
        }

        let measurement = performance::start(
            PerformanceAction::ModalClose,
            PerformanceContext::from_board(app.boards.current_board()),
        );
        app.modals.column.set(None);
        (measurement)();
    };

    let column_title = Signal::derive(move || {
        column
            .get()
            .map(|column_state| column_state.column_type.display_name().to_string())
            .unwrap_or_default()
    });

    let column_type = Signal::derive(move || {
        column
            .get()
            .map(|column_state| column_state.column_type)
            .unwrap_or_else(|| ColumnType::Todo)
    });

    let wip_limit = RwSignal::new(String::new());
    let limit_error = RwSignal::new(None::<String>);

    let modal_title = Signal::derive(move || format!("Edit Column: {}", column_title.get()));

    Effect::new(move || {
        if is_open.get() {
            limit_error.set(None);
        }
    });

    Effect::new(move || {
        if let Some(column_state) = column.get() {
            wip_limit.set(
                column_state
                    .wip_limit
                    .get()
                    .map(|limit| limit.to_string())
                    .unwrap_or_default(),
            );
        } else {
            wip_limit.set(String::new());
        }
    });

    let save_column = move || {
        let user_column = UserColumn {
            column_type: column_type.get(),
            wip_limit: wip_limit.get(),
        };

        match user_column.validate() {
            Ok(new_column) => {
                if let Some(column_state) = column.get() {
                    let measurement = performance::start(
                        PerformanceAction::ColumnEdit,
                        PerformanceContext::from_board(app.boards.current_board()),
                    );
                    column_state
                        .wip_limit
                        .set(new_column.wip_limit().to_owned());
                    close_modal_without_measurement();
                    (measurement)();
                } else {
                    close_modal_without_measurement();
                }
            }
            Err(ColumnValidationError::InvalidWipLimit) => {
                limit_error.set(Some(String::from("Please enter a valid number.")));
            }
        }
    };

    view! {
        <Modal title=modal_title is_open on_save=save_column close=close_modal>
            <Input
                label="WIP Limit"
                value=wip_limit
                input_type=InputType::Number
                error_message=Signal::derive(move || limit_error.get())
                min=0
            />
        </Modal>
    }
}
