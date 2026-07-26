use leptos::prelude::*;

use crate::{
    components::{IconButton, Input, Modal, Select, Textarea, icons::FontawesomeIcon},
    performance::{self, FinishPerformanceMeasurement, PerformanceAction, PerformanceContext},
    types::{
        app_context::AppContext,
        modals::TaskFormState,
        serialize::Task,
        state::TaskState,
        ui::{Color, InputType, Size},
    },
};

#[component]
pub fn TaskModal() -> impl IntoView {
    let app: AppContext = expect_context();
    let form = TaskFormState::new(None);

    Effect::new(move || {
        if let Some(data) = app.modals.task.get() {
            form.set_task(data.task);
        }
    });

    let close_modal = move || {
        if app.modals.task.get_untracked().is_some() {
            app.modals.task.set(None);
        }
    };
    let save_task = move || {
        let Some(data) = app.modals.task.get_untracked() else {
            return;
        };

        form.clear_errors();

        match form.user_task().validate() {
            Ok(validated_task) => {
                let finish_measurement =
                    save_validated_task(app, data.task, data.column_id, validated_task);
                close_modal();

                if let Some(finish_measurement) = finish_measurement {
                    (finish_measurement)();
                }
            }
            Err(error) => form.set_validation_error(error),
        }
    };

    let is_open = Signal::derive(move || app.modals.task.get().is_some());
    let modal_title = Signal::derive(move || {
        app.modals
            .task
            .get()
            .and_then(|data| data.task)
            .map(|_| String::from("Edit Task"))
            .unwrap_or_else(|| String::from("Add Task"))
    });
    let save_data_test_id = Signal::derive(move || {
        format!(
            "save-button-{}",
            app.modals
                .task
                .get()
                .and_then(|data| data.column_id)
                .map(|column_type| column_type.name())
                .unwrap_or("unknown-column"),
        )
    });

    view! {
        <Modal
            title=modal_title
            is_open
            on_save=save_task
            close=close_modal
            save_data_test_id
        >
            <TaskFormFields form />
        </Modal>
    }
}

#[component]
fn TaskFormFields(form: TaskFormState) -> impl IntoView {
    view! {
        <Input
            label="Title"
            value=form.title
            error_message=Signal::derive(move || form.title_error.get())
            data_test_id="task-title-input"
        />

        <Textarea label="Description" value=form.description />

        <Select
            label="Priority"
            options=vec!["Low".into(), "Medium".into(), "High".into()]
            value=form.priority
            error_message=Signal::derive(move || form.priority_error.get())
        />

        <div class="is-flex">
            <Input
                label="Due Date"
                input_type=InputType::Date
                value=form.due_date
                error_message=Signal::derive(move || form.due_date_error.get())
            />
            <div class="is-flex is-align-items-end pl-2 mb-4">
                <IconButton
                    icon=FontawesomeIcon::Reset
                    color=Color::Light
                    size=Size::Small
                    aria_label="Reset due date"
                    on_click=move || form.due_date.set(String::new())
                />
            </div>
        </div>
    }
}

fn save_validated_task(
    app: AppContext,
    edited_task: Option<TaskState>,
    column_type: Option<crate::types::serialize::ColumnType>,
    validated_task: Task,
) -> Option<FinishPerformanceMeasurement> {
    if let Some(task_state) = edited_task {
        let finish_measurement = start_task_measurement(app, PerformanceAction::TaskEdit);
        update_task(task_state, &validated_task);
        Some(finish_measurement)
    } else if let Some(column_type) = column_type {
        let finish_measurement = start_task_measurement(app, PerformanceAction::TaskCreate);
        app.boards
            .add_task_to_current_board(&column_type, TaskState::from_task(&validated_task));
        Some(finish_measurement)
    } else {
        None
    }
}

fn update_task(task_state: TaskState, validated_task: &Task) {
    task_state.title.set(validated_task.title().to_string());
    task_state
        .description
        .set(validated_task.description().cloned());
    task_state.due_date.set(validated_task.due_date().cloned());
    task_state.priority.set(*validated_task.priority());
}

fn start_task_measurement(
    app: AppContext,
    action: PerformanceAction,
) -> FinishPerformanceMeasurement {
    performance::start(
        action,
        PerformanceContext::from_board(app.boards.current_board()),
    )
}
