use leptos::prelude::*;

use crate::{
    components::{IconButton, Input, Modal, Select, Textarea, icons::FontawesomeIcon},
    performance::{self, PerformanceAction, PerformanceContext},
    types::{
        app_context::AppContext,
        format_date_to_string,
        modals::OpenTaskModal,
        state::TaskState,
        ui::{Color, InputType, Size},
        validation::task::{TaskValidationError, UserTask},
    },
};

#[component]
pub fn TaskModal() -> impl IntoView {
    let app: AppContext = expect_context();

    let is_open = Signal::derive(move || app.modals.task.get().is_some());

    let data = Signal::derive(move || app.modals.task.get().unwrap_or(OpenTaskModal::new(None)));
    let task = Signal::derive(move || data.get().task);
    let column_id = Signal::derive(move || data.get().column_id);

    let close_modal = move || app.modals.task.set(None);

    let is_edit = move || task.get().is_some();

    let title = RwSignal::new(String::new());
    let description = RwSignal::new(String::new());
    let priority = RwSignal::new(String::from("Medium"));
    let due_date = RwSignal::new(String::new());

    let title_error = RwSignal::new(None::<String>);
    let due_date_error = RwSignal::new(None::<String>);
    let priority_error = RwSignal::new(None::<String>);

    let modal_title = Signal::derive(move || {
        if is_edit() {
            "Edit Task".to_string()
        } else {
            "Add Task".to_string()
        }
    });

    Effect::new(move || {
        if is_open.get() {
            title_error.set(None);
            due_date_error.set(None);
            priority_error.set(None);
        }
    });

    Effect::new(move || {
        if let Some(task_state) = task.get() {
            title.set(task_state.title.get());
            description.set(task_state.description.get().unwrap_or_default());
            priority.set(task_state.priority.get().to_string());
            due_date.set(
                task_state
                    .due_date
                    .get()
                    .map(|date| format_date_to_string(&date))
                    .unwrap_or_default(),
            );
        } else {
            title.set(String::new());
            description.set(String::new());
            priority.set(String::from("Medium"));
            due_date.set(String::new());
        }
    });

    let save_task = move || {
        let edited_task = task.get();

        let user_task = UserTask {
            title: title.get(),
            description: description.get(),
            due_date: due_date.get(),
            priority: priority.get(),
        };

        match user_task.validate() {
            Ok(new_task) => match edited_task {
                Some(task_state) => {
                    let measurement = performance::start(
                        PerformanceAction::TaskEdit,
                        PerformanceContext::from_board(app.boards.current_board()),
                    );

                    task_state.title.set(new_task.title().to_string());
                    task_state.description.set(new_task.description().cloned());
                    task_state.due_date.set(new_task.due_date().cloned());
                    task_state.priority.set(new_task.priority().clone());
                    close_modal();
                    (measurement)();
                }
                None => {
                    let measurement = if let Some(column_type) = column_id.get_untracked() {
                        let measurement = performance::start(
                            PerformanceAction::TaskCreate,
                            PerformanceContext::from_board(app.boards.current_board()),
                        );
                        let task_state = TaskState::from_task(&new_task);
                        app.boards
                            .add_task_to_current_board(&column_type, task_state);
                        Some(measurement)
                    } else {
                        None
                    };

                    title.set(String::new());
                    description.set(String::new());
                    priority.set(String::from("Medium"));
                    due_date.set(String::new());
                    close_modal();

                    if let Some(measurement) = measurement {
                        (measurement)();
                    }
                }
            },
            Err(TaskValidationError::TitleTooLong) => {
                title_error.set(Some(String::from(
                    "Please enter a title with at most 200 characters.",
                )));
            }
            Err(TaskValidationError::EmptyTitle) => {
                title_error.set(Some(String::from("The title must not be empty.")));
            }
            Err(TaskValidationError::InvalidDueDate) => {
                due_date_error.set(Some(String::from("Please enter a valid date.")));
            }
            Err(TaskValidationError::InvalidPriority) => {
                priority_error.set(Some(String::from("Please select a valid priority.")));
            }
        }
    };

    let save_data_test_id = Signal::derive(move || format!("save-button-{}", column_id.get().map(|column| {
        column.name()
    }).unwrap_or_else(|| "unknown-column")));

    view! {
        <Modal 
            title=modal_title 
            is_open 
            on_save=save_task 
            close=close_modal 
            save_data_test_id
        >
            <Input
                label="Title"
                value=title
                error_message=Signal::derive(move || title_error.get())
                data_test_id="task-title-input"
            />

            <Textarea
                label="Description"
                value=description
            />

            <Select
                label="Priority"
                options=vec!["Low".into(), "Medium".into(), "High".into()]
                value=priority
                error_message=Signal::derive(move || priority_error.get())
            />

            <div class="is-flex">
                <Input
                    label="Due Date"
                    input_type=InputType::Date
                    value=due_date
                    error_message=Signal::derive(move || due_date_error.get())
                />
                <div class="is-flex is-align-items-end pl-2 mb-4">
                    <IconButton
                        icon=FontawesomeIcon::Reset
                        color=Color::Light
                        size=Size::Small
                        aria_label="Reset due date"
                        on_click=move || {
                            due_date.set(String::new());
                        }
                    />
                </div>
            </div>
        </Modal>
    }
}
