use leptos::prelude::*;
use time::Date;

use crate::types::serialize::{Priority, Task, TaskId};

#[derive(Clone, Copy, Debug)]
pub struct TaskState {
    pub id: TaskId,
    pub title: RwSignal<String>,
    pub description: RwSignal<Option<String>>,
    pub due_date: RwSignal<Option<Date>>,
    pub priority: RwSignal<Priority>,
}

impl TaskState {
    pub fn from_task(task: &Task) -> Self {
        task.into()
    }
}

impl From<&Task> for TaskState {
    fn from(task: &Task) -> Self {
        Self {
            id: task.id(),
            title: RwSignal::new(task.title().to_string()),
            description: RwSignal::new(task.description().cloned()),
            due_date: RwSignal::new(task.due_date().cloned()),
            priority: RwSignal::new(task.priority().clone()),
        }
    }
}
