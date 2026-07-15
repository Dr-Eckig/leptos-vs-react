use crate::components::icons::FontawesomeIcon;
use crate::components::{DraggableItem, DropZone, IconButton, Tag, TaskCard};
use crate::performance::{self, PerformanceAction, PerformanceContext};
use crate::types::app_context::AppContext;
use crate::types::drag_and_drop::DraggableItemDto;
use crate::types::modals::{OpenColumnModal, OpenTaskModal};
use crate::types::serialize::{ColumnType, TaskId};
use crate::types::state::{ColumnState, TaskState};
use crate::types::ui::{ButtonState, Color, Size};
use leptos::prelude::*;

#[component]
pub fn TaskColumn(column: ColumnState) -> impl IntoView {
    let app: AppContext = expect_context();

    let column_name = Signal::derive(move || column.column_type.name().to_string());
    let tasks = Signal::derive(move || column.tasks.get());
    let drop_allowed = Signal::derive(move || {
        app.drag_and_drop
            .dragged_item
            .get()
            .map(|dragged_item| column.can_accept_task_from(dragged_item.source_column_type))
            .unwrap_or(true)
    });

    let move_task_to_column_end = Callback::new(move |dragged_item| {
        move_task(app, column.column_type, dragged_item, None);
    });

    view! {
        <div class="column is-flex is-flex-direction-column">
            <DropZone
                class="kanban-column-drop-zone box is-radiusless full-height scrollable p-0"
                data_test_id=Signal::derive(move || {
                    format!("{}-column-drop-zone", column.column_type.name())
                })
                on_drop=move_task_to_column_end
                drop_allowed
            >
                <TaskColumnHeader column />

                <ForEnumerate
                    each=move || tasks.get()
                    key=|task| task.id
                    children=move |task_index, task| {
                        view! {
                            <TaskDropTarget
                                column
                                task
                                task_index
                                column_name
                                drop_allowed
                            />
                        }
                    }
                />
            </DropZone>
        </div>
    }
}

#[component]
fn TaskColumnHeader(column: ColumnState) -> impl IntoView {
    let app: AppContext = expect_context();

    let column_title = move || column.column_type.display_name();
    let task_count = Signal::derive(move || column.tasks.get().len());
    let wip_limit = Signal::derive(move || column.wip_limit.get());
    let is_wip_limit_reached = Signal::derive(move || column.wip_limit_reached());

    let tag_text = Signal::derive(move || {
        let count = task_count.get();

        match wip_limit.get() {
            Some(limit) => format!("{count} / {limit}"),
            None => count.to_string(),
        }
    });

    let tag_color = Signal::derive(move || {
        if is_wip_limit_reached.get() {
            Color::Danger
        } else {
            Color::Light
        }
    });

    let add_button_state = Signal::derive(move || {
        if is_wip_limit_reached.get() {
            ButtonState::Disabled
        } else {
            ButtonState::default()
        }
    });

    view! {
        <div class="is-flex is-justify-content-space-between is-align-items-center is-sticky p-4">
            <div class="is-flex is-align-items-center">
                <Tag text=tag_text color=tag_color is_rounded=true />
                <p class="title is-4 pl-2"> { column_title } </p>
            </div>
            <div class="buttons">
                <IconButton
                    icon=FontawesomeIcon::Edit
                    color=Color::Warning
                    size=Size::Small
                    aria_label="Edit column"
                    on_click=move || {
                        app.modals.column.set(Some(OpenColumnModal::new_with_column(column)));
                    }
                />
                <IconButton
                    icon=FontawesomeIcon::Plus
                    color=Color::Link
                    size=Size::Small
                    state=add_button_state
                    aria_label="Add task"
                    data_test_id=Signal::derive(move || {
                        format!("add-task-button-{}", column.column_type.name())
                    })
                    on_click=move || {
                        app.modals.task.set(Some(OpenTaskModal::new(Some(column.column_type))));
                    }
                />
            </div>
        </div>
    }
}

#[component]
fn TaskDropTarget(
    column: ColumnState,
    task: TaskState,
    task_index: ReadSignal<usize>,
    column_name: Signal<String>,
    drop_allowed: Signal<bool>,
) -> impl IntoView {
    let app: AppContext = expect_context();

    let on_edit = Callback::new(move |_| {
        app.modals
            .task
            .set(Some(OpenTaskModal::new_with_task(column.column_type, task)));
    });

    let on_delete = Callback::new(move |_| {
        app.boards.delete_task_from_current_board(&task.id);
    });

    let on_drop = Callback::new(move |dragged_item| {
        move_task(app, column.column_type, dragged_item, Some(task.id));
    });

    view! {
        <DropZone
            class="kanban-task-drop-target"
            data_test_id=Signal::derive(move || {
                format!(
                    "{}-task-drop-target-{}",
                    column.column_type.name(),
                    task_index.get(),
                )
            })
            on_drop
            drop_allowed
        >
            <DraggableItem
                data=DraggableItemDto::new(task.id, column.column_type)
                data_test_id=Signal::derive(move || {
                    format!(
                        "{}-task-draggable-{}",
                        column.column_type.name(),
                        task_index.get(),
                    )
                })
            >
                <TaskCard
                    task
                    column_name
                    task_index
                    on_edit
                    on_delete
                />
            </DraggableItem>
        </DropZone>
    }
}

fn move_task(
    app: AppContext,
    target_column_type: ColumnType,
    dragged_item: DraggableItemDto,
    before_task_id: Option<TaskId>,
) {
    let measurement = performance::start(
        move_performance_action(dragged_item.source_column_type, target_column_type),
        PerformanceContext::from_board(app.boards.current_board()),
    );

    if app.boards.move_task_in_current_board(
        &dragged_item.task_id,
        &target_column_type,
        before_task_id,
    ) {
        (measurement)();
    }
}

fn move_performance_action(
    source_column_type: ColumnType,
    target_column_type: ColumnType,
) -> PerformanceAction {
    if source_column_type == target_column_type {
        PerformanceAction::TaskMoveWithinColumn
    } else {
        PerformanceAction::TaskMoveBetweenColumns
    }
}
