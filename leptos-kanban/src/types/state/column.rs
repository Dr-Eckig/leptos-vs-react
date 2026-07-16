use leptos::prelude::*;

use crate::types::{
    serialize::{Column, ColumnId, ColumnType, TaskId},
    state::task::TaskState,
};

#[derive(Clone, Copy, Debug)]
pub struct ColumnState {
    pub id: ColumnId,
    pub column_type: ColumnType,
    pub tasks: RwSignal<Vec<TaskState>>,
    pub wip_limit: RwSignal<Option<u32>>,
}

impl ColumnState {
    pub fn can_accept_task_from(&self, source_column_type: ColumnType) -> bool {
        if self.column_type == source_column_type {
            return true;
        }

        !self.wip_limit_reached()
    }

    pub fn wip_limit_reached(&self) -> bool {
        match self.wip_limit.get() {
            Some(limit) => self.tasks.with(|tasks| tasks.len() >= limit as usize),
            None => false,
        }
    }

    pub fn has_task(&self, task_id: &TaskId) -> bool {
        self.tasks
            .with(|tasks| tasks.iter().any(|task| &task.id == task_id))
    }

    pub fn remove_task(&self, task_id: &TaskId) -> Option<TaskState> {
        let mut removed_task = None;

        self.tasks.update(|tasks| {
            if let Some(task_index) = tasks.iter().position(|task| &task.id == task_id) {
                removed_task = Some(tasks.remove(task_index));
            }
        });

        removed_task
    }

    pub fn move_task(&self, task_id: &TaskId, before_task_id: Option<TaskId>) -> bool {
        let mut moved = false;

        self.tasks.update(|tasks| {
            let Some(task_index) = tasks.iter().position(|task| &task.id == task_id) else {
                return;
            };

            let task = tasks.remove(task_index);
            let insert_index = before_task_id
                .and_then(|before_task_id| tasks.iter().position(|task| task.id == before_task_id))
                .unwrap_or(tasks.len());

            tasks.insert(insert_index, task);
            moved = true;
        });

        moved
    }

    pub fn insert_task(&self, task: TaskState, before_task_id: Option<TaskId>) {
        self.tasks.update(|tasks| {
            let insert_index = before_task_id
                .and_then(|task_id| tasks.iter().position(|task| task.id == task_id))
                .unwrap_or(tasks.len());

            tasks.insert(insert_index, task);
        });
    }
}

impl From<&Column> for ColumnState {
    fn from(column: &Column) -> Self {
        Self {
            id: column.id(),
            column_type: column.column_type(),
            tasks: RwSignal::new(column.tasks().iter().map(TaskState::from).collect()),
            wip_limit: RwSignal::new(*column.wip_limit()),
        }
    }
}
