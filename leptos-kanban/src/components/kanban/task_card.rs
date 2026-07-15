use leptos::prelude::*;

use crate::components::icons::FontawesomeIcon;
use crate::components::{Dropdown, IconText, Tag};
use crate::performance::{self, PerformanceAction, PerformanceContext};
use crate::types::app_context::AppContext;
use crate::types::format_date_to_display;
use crate::types::serialize::Priority;
use crate::types::state::TaskState;
use crate::types::ui::{Alignment, Color};

#[component]
pub fn TaskCard(
    task: TaskState,
    task_index: ReadSignal<usize>,
    #[prop(into)] column_name: Signal<String>,
    on_edit: Callback<()>,
    on_delete: Callback<()>,
) -> impl IntoView {
    view! {
        <div class=move || {
            format!(
                "card m-4 {}",
                priority_border_class(task.priority.get()),
            )
        }>
            <TaskCardHeader
                task
                task_index
                column_name
                on_edit
                on_delete
            />
            <TaskCardContent task />
        </div>
    }
}

#[component]
fn TaskCardHeader(
    task: TaskState,
    task_index: ReadSignal<usize>,
    column_name: Signal<String>,
    on_edit: Callback<()>,
    on_delete: Callback<()>,
) -> impl IntoView {
    view! {
        <header class="card-header">
            <p class="card-header-title">
                <span class="pr-2"> { move || task.title.get() } </span>
            </p>
            <TaskActionsDropdown
                task_index
                column_name
                on_edit
                on_delete
            />
        </header>
    }
}

#[component]
fn TaskActionsDropdown(
    task_index: ReadSignal<usize>,
    column_name: Signal<String>,
    on_edit: Callback<()>,
    on_delete: Callback<()>,
) -> impl IntoView {
    let app: AppContext = expect_context();
    let is_visible = RwSignal::new(false);
    let data_test_id =
        Signal::derive(move || format!("{}-task-dropdown-{}", column_name.get(), task_index.get()));

    let edit_task = move |_| {
        on_edit.run(());
        is_visible.set(false);
    };
    let delete_task = move |_| {
        let finish_measurement = performance::start(
            PerformanceAction::TaskDelete,
            PerformanceContext::from_board(app.boards.current_board()),
        );
        on_delete.run(());
        is_visible.set(false);
        (finish_measurement)();
    };

    view! {
        <Dropdown
            is_visible
            alignment=Alignment::Right
            trigger=Box::new(move || {
                view! {
                    <button
                        class="card-header-icon"
                        aria-label="options"
                        data-testid=data_test_id
                        on:click=move |_| is_visible.update(|visible| *visible = !*visible)
                    >
                        <span class="icon">
                            <i class=FontawesomeIcon::EllipsisVertical.as_fontawesome()></i>
                        </span>
                    </button>
                }.into_any()
            })
        >
            <button
                class="dropdown-item"
                data-testid=move || format!("{}-edit", data_test_id.get())
                on:click=edit_task
            >
                <IconText icon=FontawesomeIcon::Edit text="Edit" color=Color::Warning />
            </button>
            <button
                class="dropdown-item"
                data-testid=move || format!("{}-delete", data_test_id.get())
                on:click=delete_task
            >
                <IconText icon=FontawesomeIcon::Trash text="Delete" color=Color::Danger />
            </button>
        </Dropdown>
    }
}

#[component]
fn TaskCardContent(task: TaskState) -> impl IntoView {
    let due_date = Signal::derive(move || task.due_date.get());
    let priority = Signal::derive(move || task.priority.get());
    let due_date_text = Signal::derive(move || {
        due_date
            .get()
            .map(|date| format_date_to_display(&date))
            .unwrap_or_default()
    });

    view! {
        <div class="card-content">
            <div class="tags mb-2">
                <Tag
                    text=Signal::derive(move || priority.get().to_string())
                    color=Signal::derive(move || priority_color(priority.get()))
                />
                <Show when=move || due_date.get().is_some()>
                    <Tag text=due_date_text />
                </Show>
            </div>
            <p> { move || task.description.get().unwrap_or_default() } </p>
        </div>
    }
}

fn priority_color(priority: Priority) -> Color {
    match priority {
        Priority::Low => Color::Success,
        Priority::Medium => Color::Warning,
        Priority::High => Color::Danger,
    }
}

fn priority_border_class(priority: Priority) -> &'static str {
    match priority {
        Priority::Low => "border-color-success",
        Priority::Medium => "border-color-warning",
        Priority::High => "border-color-danger",
    }
}
