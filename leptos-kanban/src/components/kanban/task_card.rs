use leptos::prelude::*;

use crate::components::icons::FontawesomeIcon;
use crate::components::{Dropdown, IconText, Tag};
use crate::types::format_date_to_display;
use crate::types::ui::{Alignment, Color};
use crate::types::state::TaskState;
use crate::types::serialize::Priority;

#[component]
pub fn TaskCard(
    task: TaskState,
    task_index: ReadSignal<usize>,
    #[prop(into)] column_name: Signal<String>,
    on_edit: Callback<()>, 
    on_delete: Callback<()>, 
) -> impl IntoView {
    let title = move || task.title.get();
    let description = move || task.description.get();
    let due_date = Signal::derive(move || task.due_date.get());
    let priority = Signal::derive(move || task.priority.get());

    let due_date_text = Signal::derive(move || {
        due_date
            .get()
            .map(|date| format_date_to_display(&date))
            .unwrap_or_default()
    });

    let dropdown_visible = RwSignal::new(false);

    let priority_color = Signal::derive(move || match priority.get() {
        Priority::Low => Color::Success,
        Priority::Medium => Color::Warning,
        Priority::High => Color::Danger,
    });

    let card_border = Signal::derive(move || match priority.get() {
        Priority::Low => "border-color-success",
        Priority::Medium => "border-color-warning",
        Priority::High => "border-color-danger",
    });

    let dropdown_data_test_id = Signal::derive(move || format!("{}-task-dropdown-{}", column_name.get(), task_index.get()));

    view! {
        <div class=move || format!("card m-4 {}", card_border.get())>
            <header class="card-header">
                <p class="card-header-title">
                    <span class="pr-2"> { title } </span>
                </p>
                <Dropdown
                    is_visible=dropdown_visible
                    alignment=Alignment::Right
                    trigger=Box::new(move || {
                        view! {
                            <button
                                class="card-header-icon"
                                aria-label="options"
                                data-testid=dropdown_data_test_id
                                on:click=move |_| dropdown_visible.set(!dropdown_visible.get())
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
                        data-testid=move || format!("{}-edit", dropdown_data_test_id.get())
                        on:click=move |_| {
                            dropdown_visible.set(false);
                            on_edit.run(());
                        }
                    >
                        <IconText
                            icon=FontawesomeIcon::Edit
                            text="Edit"
                            color=Color::Warning
                        />
                    </button>
                    <button
                        class="dropdown-item"
                        data-testid=move || format!("{}-delete", dropdown_data_test_id.get())
                        on:click=move |_| {
                            dropdown_visible.set(false);
                            on_delete.run(());
                        }
                    >
                        <IconText
                            icon=FontawesomeIcon::Trash
                            text="Delete"
                            color=Color::Danger
                        />
                    </button>
                </Dropdown>

            </header>
            <div class="card-content">
                <div class="tags mb-2">
                    <Tag
                        text=Signal::derive(move || priority.get().to_string())
                        color=priority_color
                    />
                    <Show when=move || due_date.get().is_some()>
                        <Tag
                            text=due_date_text
                        />
                    </Show>
                </div>
                <p> { description } </p>
            </div>
        </div>
    }
}
