use leptos::{html::Div, prelude::*};
use leptos_use::on_click_outside;

use crate::{components::ui::{Button, icons::FontawesomeIcon}, types::ui::Color};

#[component]
pub fn Modal<CloseFunction, SaveFunction>(
    #[prop(into)] title: Signal<String>,
    is_open: Signal<bool>,
    close: CloseFunction,
    children: Children,
    #[prop(optional, into)] save_data_test_id: Signal<String>,
    on_save: SaveFunction,
    #[prop(optional, into)] on_delete: MaybeProp<Callback<()>>,
) -> impl IntoView
where
    CloseFunction: Fn() + Clone + Copy + 'static,
    SaveFunction: Fn() + 'static,
{
    let modal_area = NodeRef::<Div>::new();
    let _ = on_click_outside(modal_area, move |_| close());

    view! {
        <div class="modal" class:is-active=move || is_open.get()>
            <div class="modal-background"></div>
            <div class="modal-card" node_ref=modal_area>
                <header class="modal-card-head">
                    <p class="modal-card-title"> { move || title.get() } </p>
                    <button class="delete" aria-label="close" on:click=move |_| close() />
                </header>
                <section class="modal-card-body">
                    { children() }
                </section>
                <footer class=move || format!("modal-card-foot is-flex {}", if on_delete.get().is_some() { "is-justify-content-space-between" } else { "is-justify-content-flex-end" })>
                    <Show when=move || on_delete.get().is_some()>
                        <Button
                            text="Delete"
                            icon=FontawesomeIcon::Trash
                            color=Color::Danger
                            aria_label="Delete"
                            on_click=move || {
                                if let Some(on_delete) = on_delete.get() {
                                    on_delete.run(());
                                }
                            }
                        />
                    </Show>
                    <div>
                        <div class="buttons">
                            <Button
                                text="Save"
                                color=Color::Success
                                aria_label="Save"
                                data_test_id=save_data_test_id
                                on_click=on_save
                            />
                            <Button
                                text="Cancel"
                                color=Color::Light
                                aria_label="Cancel"
                                on_click=move || close()
                            />
                        </div>
                    </div>
                </footer>
            </div>
        </div>
    }
}
