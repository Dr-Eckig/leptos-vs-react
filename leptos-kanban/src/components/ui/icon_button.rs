use leptos::prelude::*;

use crate::{
    components::ui::icons::FontawesomeIcon,
    types::ui::{ButtonState, Color, Size},
};

#[component]
pub fn IconButton<F>(
    #[prop(into)] icon: Signal<FontawesomeIcon>,
    #[prop(into, optional)] color: Signal<Color>,
    #[prop(into, optional)] size: Signal<Size>,
    #[prop(into, optional)] state: Signal<ButtonState>,
    #[prop(into)] aria_label: String,
    #[prop(into, optional)] data_test_id: Signal<String>,
    on_click: F,
) -> impl IntoView
where
    F: Fn() + 'static,
{
    let is_disabled = move || matches!(state.get(), ButtonState::Disabled);

    let button_class = move || {
        format!(
            "button {} {} {}",
            color.get().as_class(),
            size.get().as_class(),
            state.get().as_class(),
        )
    };

    let icon_class = move || format!("{} {}", icon.get().as_fontawesome(), size.get().as_class());

    view! {
        <button
            class=button_class
            disabled=is_disabled
            aria-label=aria_label
            data-testid=data_test_id
            on:click=move |_| on_click()
        >
            <span class="icon">
                <i class=icon_class></i>
            </span>
        </button>
    }
}
