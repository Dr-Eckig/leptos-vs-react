use leptos::{html::Div, prelude::*};
use leptos_use::on_click_outside;

use crate::types::ui::Alignment;

pub type Trigger = Box<dyn FnOnce() -> AnyView + Send>;

#[component]
pub fn Dropdown(
    #[prop(into)] is_visible: RwSignal<bool>,
    trigger: Trigger,
    #[prop(optional)] alignment: Alignment,
    children: Children,
) -> impl IntoView {
    let dropdown_class = format!("dropdown {}", alignment.as_class());

    let dropdown_area = NodeRef::<Div>::new();
    let _ = on_click_outside(dropdown_area, move |_| is_visible.set(false));

    view! {
        <div class=dropdown_class class:is-active=move || is_visible.get() node_ref=dropdown_area>
            <div class="dropdown-trigger">
                { trigger() }
            </div>
            <div class="dropdown-menu" id="dropdown-menu" role="menu">
                <div class="dropdown-content">
                    { children() }
                </div>
            </div>
        </div>
    }
}
