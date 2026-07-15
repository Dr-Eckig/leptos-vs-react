use leptos::prelude::*;

use crate::{
    components::{IconButton, Input, Modal, Select, Textarea, icons::FontawesomeIcon},
    performance::{self, FinishPerformanceMeasurement, PerformanceAction, PerformanceContext},
    types::{
        app_context::AppContext,
        format_date_to_string,
        modals::OpenTaskModal,
        serialize::Task,
        state::TaskState,
        ui::{Color, InputType, Size},
        validation::task::{TaskValidationError, UserTask},
    },
};

#[derive(Clone, Copy)]
struct TaskFormState {
    title: RwSignal<String>,
    description: RwSignal<String>,
    priority: RwSignal<String>,
    due_date: RwSignal<String>,
    title_error: RwSignal<Option<String>>,
    priority_error: RwSignal<Option<String>>,
    due_date_error: RwSignal<Option<String>>,
}

impl TaskFormState {
    fn new(task: Option<TaskState>) -> Self {
        Self {
            title: RwSignal::new(
                task.map(|task| task.title.get_untracked())
                    .unwrap_or_default(),
            ),
            description: RwSignal::new(
                task.and_then(|task| task.description.get_untracked())
                    .unwrap_or_default(),
            ),
            priority: RwSignal::new(
                task.map(|task| task.priority.get_untracked().to_string())
                    .unwrap_or_else(|| String::from("Medium")),
            ),
            due_date: RwSignal::new(
                task.and_then(|task| task.due_date.get_untracked())
                    .map(|date| format_date_to_string(&date))
                    .unwrap_or_default(),
            ),
            title_error: RwSignal::new(None),
            priority_error: RwSignal::new(None),
            due_date_error: RwSignal::new(None),
        }
    }

    fn user_task(self) -> UserTask {
        UserTask {
            title: self.title.get_untracked(),
            description: self.description.get_untracked(),
            due_date: self.due_date.get_untracked(),
            priority: self.priority.get_untracked(),
        }
    }

    fn clear_errors(self) {
        self.title_error.set(None);
        self.priority_error.set(None);
        self.due_date_error.set(None);
    }

    fn set_validation_error(self, error: TaskValidationError) {
        match error {
            TaskValidationError::TitleTooLong => self.title_error.set(Some(String::from(
                "Please enter a title with at most 200 characters.",
            ))),
            TaskValidationError::EmptyTitle => self
                .title_error
                .set(Some(String::from("The title must not be empty."))),
            TaskValidationError::InvalidDueDate => self
                .due_date_error
                .set(Some(String::from("Please enter a valid date."))),
            TaskValidationError::InvalidPriority => self
                .priority_error
                .set(Some(String::from("Please select a valid priority."))),
        }
    }
}

#[component]
pub fn TaskModal() -> impl IntoView {
    let app: AppContext = expect_context();

    view! {
        {move || {
            app.modals
                .task
                .get()
                .map(|data| view! { <TaskModalContent data /> })
        }}
    }
}

#[component]
fn TaskModalContent(data: OpenTaskModal) -> impl IntoView {
    let app: AppContext = expect_context();
    let task = data.task;
    let column_type = data.column_id;
    let form = TaskFormState::new(task);

    let close_modal = move || app.modals.task.set(None);
    let save_task = move || {
        form.clear_errors();

        match form.user_task().validate() {
            Ok(validated_task) => {
                let finish_measurement =
                    save_validated_task(app, task, column_type, validated_task);
                close_modal();

                if let Some(finish_measurement) = finish_measurement {
                    (finish_measurement)();
                }
            }
            Err(error) => form.set_validation_error(error),
        }
    };

    let modal_title = if task.is_some() {
        "Edit Task"
    } else {
        "Add Task"
    };
    let save_data_test_id = format!(
        "save-button-{}",
        column_type
            .map(|column_type| column_type.name())
            .unwrap_or("unknown-column"),
    );

    view! {
        <Modal
            title=modal_title
            is_open=Signal::derive(move || true)
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
