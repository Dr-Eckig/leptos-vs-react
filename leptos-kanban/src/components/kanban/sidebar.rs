use leptos::prelude::*;

use crate::components::IconText;
use crate::components::icons::FontawesomeIcon;
use crate::performance::{self, PerformanceAction, PerformanceContext};
use crate::types::{app_context::AppContext, modals::OpenBoardModal};

#[component]
pub fn Sidebar() -> impl IntoView {
    let app: AppContext = expect_context();

    let boards = Signal::derive(move || app.boards.boards.get());

    view! {
        <aside class="menu has-background-light px-3 py-5">
            <ul class="menu-list">
                <SidebarItem
                    label="Add Board"
                    icon=FontawesomeIcon::CirclePlus
                    is_active=false
                    data_test_id="add-board-button"
                    on_click=Callback::new(move |_| {
                        let measurement = performance::start(
                            PerformanceAction::ModalOpen,
                            PerformanceContext::from_board(app.boards.current_board()),
                        );
                        app.modals.board.set(Some(OpenBoardModal::new()));
                        (measurement)();
                    })
                />
            </ul>
            <p class="menu-label">
                Boards
            </p>
            <ul class="menu-list">
                <ForEnumerate
                    each=move || boards.get()
                    key=|board| board.id
                    children={move |index, board| {
                        let id = board.id;
                        let is_active = Signal::derive(move || app.boards.current_board_id.get() == Some(id));

                        let on_edit = Callback::new(move |_| {
                            let measurement = performance::start(
                                PerformanceAction::ModalOpen,
                                PerformanceContext::from_board(app.boards.current_board()),
                            );
                            app.modals.board.set(Some(OpenBoardModal::new_with_board(board)));
                            (measurement)();
                        });

                        let on_click = Callback::new(move |_| {
                            if app.boards.current_board_id.get_untracked() == Some(id) {
                                return;
                            }

                            let measurement = performance::start(
                                PerformanceAction::BoardSwitch,
                                PerformanceContext::from_board(Some(board)),
                            );
                            app.boards.set_current_board(id);
                            (measurement)();
                        });

                        let data_test_id = Signal::derive(move || format!("sidebar-board-{}", index.get()));

                        view! {
                            <SidebarItem
                                label=board.title
                                data_test_id
                                is_active
                                on_edit
                                on_click
                            />
                        }
                    }}
                />
            </ul>
        </aside>
    }
}

#[component]
fn SidebarItem(
    #[prop(into)] label: Signal<String>,
    #[prop(optional)] icon: Option<FontawesomeIcon>,
    #[prop(into)] is_active: Signal<bool>,
    #[prop(into)] data_test_id: Signal<String>,
    #[prop(optional)] on_edit: Option<Callback<()>>,
    on_click: Callback<()>,
) -> impl IntoView {
    let html_class = move || {
        if is_active.get() {
            "has-background-link is-active"
        } else {
            "has-background-light"
        }
    };

    view! {
        <li class="sidebar-item">
            <button class=html_class data-testid=data_test_id on:click=move |_| on_click.run(())>
                {
                    match icon {
                        Some(icon) => view! {
                            <IconText icon text=label />
                        }.into_any(),

                        None => {
                            let edit_icon = on_edit.map(|on_edit| {
                                view! {
                                    <div
                                        class="edit-button ml-2"
                                        on:click=move |ev| {
                                            ev.stop_propagation();
                                            on_edit.run(());
                                        }
                                    >
                                        <i class=FontawesomeIcon::Ellipsis.as_fontawesome() />
                                    </div>
                                }
                            });

                            view! {
                                <div class="is-flex is-justify-content-space-between">
                                    {move || label.get()}

                                    { edit_icon }
                                </div>
                            }.into_any()
                        }
                    }
                }
            </button>
        </li>
    }
}
