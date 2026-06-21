use thiserror::Error;
use std::str::FromStr;

use crate::types::{normalize_optional_string, parse_date_from_string, serialize::{Priority, Task}};


#[derive(Debug, Error)]
pub enum TaskValidationError {
    #[error("Task must not be empty.")]
    EmptyTitle,

    #[error("Task title must not be longer than 200 characters.")]
    TitleTooLong,

    #[error("Due date is invalid.")]
    InvalidDueDate,

    #[error("Priority is invalid.")]
    InvalidPriority,
}

// This struct represents the data of a task that is provided by the user.
#[derive(Debug, Clone, PartialEq)]
pub struct UserTask {
    pub title: String,
    pub description: String,
    pub due_date: String,
    pub priority: String,
}

impl UserTask {
    pub fn validate(&self) -> Result<Task, TaskValidationError> {
        let title = validate_title_value(&self.title)?;
        let description = normalize_optional_string(self.description.clone());

        let due_date = match self.due_date.trim() {
            "" => None,
            due_date => Some(
                parse_date_from_string(due_date)
                    .map_err(|_| TaskValidationError::InvalidDueDate)?,
            ),
        };

        let priority = Priority::from_str(self.priority.trim())
            .map_err(|_| TaskValidationError::InvalidPriority)?;

        Ok(Task::new(title, description, due_date, priority))
    }
}

fn validate_title_value(title: &str) -> Result<String, TaskValidationError> {
    if title.trim().is_empty() {
        return Err(TaskValidationError::EmptyTitle);
    }

    if title.len() > 200 {
        return Err(TaskValidationError::TitleTooLong);
    }

    Ok(String::from(title.trim()))
}
