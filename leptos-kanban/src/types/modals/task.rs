use leptos::prelude::*;

use crate::types::{
    format_date_to_string,
    serialize::ColumnType,
    state::TaskState,
    validation::task::{TaskValidationError, UserTask},
};

#[derive(Clone)]
pub struct OpenTaskModal {
    pub column_id: Option<ColumnType>,
    pub task: Option<TaskState>,
}

impl OpenTaskModal {
    pub fn new(column_id: Option<ColumnType>) -> Self {
        Self {
            column_id,
            task: None,
        }
    }

    pub fn new_with_task(column_id: ColumnType, task: TaskState) -> Self {
        Self {
            column_id: Some(column_id),
            task: Some(task),
        }
    }
}

#[derive(Clone, Copy)]
pub struct TaskFormState {
    pub title: RwSignal<String>,
    pub description: RwSignal<String>,
    pub priority: RwSignal<String>,
    pub due_date: RwSignal<String>,
    pub title_error: RwSignal<Option<String>>,
    pub priority_error: RwSignal<Option<String>>,
    pub due_date_error: RwSignal<Option<String>>,
}

impl TaskFormState {
    pub fn new(task: Option<TaskState>) -> Self {
        let form = Self {
            title: RwSignal::new(String::new()),
            description: RwSignal::new(String::new()),
            priority: RwSignal::new(String::new()),
            due_date: RwSignal::new(String::new()),
            title_error: RwSignal::new(None),
            priority_error: RwSignal::new(None),
            due_date_error: RwSignal::new(None),
        };
        form.set_task(task);
        form
    }

    pub fn set_task(self, task: Option<TaskState>) {
        self.title.set(
            task.map(|task| task.title.get_untracked())
                .unwrap_or_default(),
        );
        self.description.set(
            task.and_then(|task| task.description.get_untracked())
                .unwrap_or_default(),
        );
        self.priority.set(
            task.map(|task| task.priority.get_untracked().to_string())
                .unwrap_or_else(|| String::from("Medium")),
        );
        self.due_date.set(
            task.and_then(|task| task.due_date.get_untracked())
                .map(|date| format_date_to_string(&date))
                .unwrap_or_default(),
        );
        self.clear_errors();
    }

    pub fn user_task(self) -> UserTask {
        UserTask {
            title: self.title.get_untracked(),
            description: self.description.get_untracked(),
            due_date: self.due_date.get_untracked(),
            priority: self.priority.get_untracked(),
        }
    }

    pub fn clear_errors(self) {
        self.title_error.set(None);
        self.priority_error.set(None);
        self.due_date_error.set(None);
    }

    pub fn set_validation_error(self, error: TaskValidationError) {
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
