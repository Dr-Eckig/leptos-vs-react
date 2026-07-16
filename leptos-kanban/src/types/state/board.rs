use leptos::prelude::*;

use crate::types::{
    serialize::{Board, BoardId, ColumnType, TaskId},
    state::{column::ColumnState, task::TaskState},
};

#[derive(Clone, Copy, Debug)]
pub struct BoardState {
    pub id: BoardId,
    pub title: RwSignal<String>,
    pub columns: RwSignal<Vec<ColumnState>>,
}

impl BoardState {
    pub fn from_board(board: &Board) -> Self {
        board.into()
    }

    pub fn add_task_to_column(&self, column_type: &ColumnType, task: TaskState) {
        let column = self.columns.with(|columns| {
            columns
                .iter()
                .copied()
                .find(|column| &column.column_type == column_type)
        });

        if let Some(column) = column {
            column.tasks.update(|tasks| tasks.push(task));
        }
    }

    pub fn delete_task(&self, task_id: &TaskId) {
        let target_column = self.columns.with(|columns| {
            columns.iter().copied().find(|column| {
                column
                    .tasks
                    .with(|tasks| tasks.iter().any(|task| &task.id == task_id))
            })
        });

        if let Some(column) = target_column {
            column
                .tasks
                .update(|tasks| tasks.retain(|task| &task.id != task_id));
        }
    }

    pub fn move_task(
        &self,
        task_id: &TaskId,
        to_column_type: &ColumnType,
        before_task_id: Option<TaskId>,
    ) -> bool {
        if before_task_id.as_ref() == Some(task_id) {
            return false;
        }

        let source_column = self.find_column_containing_task(task_id);
        let target_column = self.find_column_by_type(to_column_type);

        let (Some(source_column), Some(target_column)) = (source_column, target_column) else {
            return false;
        };

        if !target_column.can_accept_task_from(source_column.column_type) {
            return false;
        }

        if source_column.id == target_column.id {
            return source_column.move_task(task_id, before_task_id);
        }

        let Some(task) = source_column.remove_task(task_id) else {
            return false;
        };

        target_column.insert_task(task, before_task_id);
        true
    }

    fn find_column_by_type(&self, column_type: &ColumnType) -> Option<ColumnState> {
        self.columns.with(|columns| {
            columns
                .iter()
                .copied()
                .find(|column| &column.column_type == column_type)
        })
    }

    fn find_column_containing_task(&self, task_id: &TaskId) -> Option<ColumnState> {
        self.columns.with(|columns| {
            columns
                .iter()
                .copied()
                .find(|column| column.has_task(task_id))
        })
    }
}

impl From<&Board> for BoardState {
    fn from(board: &Board) -> Self {
        Self {
            id: board.id(),
            title: RwSignal::new(board.title().to_string()),
            columns: RwSignal::new(board.columns().iter().map(ColumnState::from).collect()),
        }
    }
}
