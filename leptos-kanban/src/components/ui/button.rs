use leptos::prelude::*;

use crate::{
    components::icons::FontawesomeIcon,
    types::ui::{ButtonState, Color, Size},
};

#[component]
pub fn Button<F>(
    #[prop(into)] text: Signal<String>,
    #[prop(into, optional)] icon: Signal<Option<FontawesomeIcon>>,
    #[prop(into, optional)] color: Signal<Color>,
    #[prop(into, optional)] size: Signal<Size>,
    #[prop(into, optional)] state: Signal<ButtonState>,
    #[prop(default=false)] is_fullwidth: bool,
    #[prop(into)] aria_label: String,
    #[prop(into, optional)] data_test_id: Signal<String>,
    on_click: F,
) -> impl IntoView
where
    F: Fn() + 'static,
{
    let button_class = move || {
        format!(
            "button {} {} {} {}",
            color.get().as_class(),
            size.get().as_class(),
            state.get().as_class(),
            is_fullwidth.then(|| "is-fullwidth").unwrap_or_default(),
        )
    };

    let is_disabled = move || matches!(state.get(), ButtonState::Disabled);

    view! {
        <button
            class=button_class
            disabled=is_disabled
            aria-label=aria_label
            data-testid=data_test_id
            on:click=move |_| on_click()
        >
            { move || icon.get().map(|icon| {
                let icon_class = move || format!("{} {}", icon.as_fontawesome(), size.get().as_class());
                view! {
                    <span class="icon">
                        <i class=icon_class></i>
                    </span>
                }
            }) }
            <span>{ text }</span>
        </button>
    }
}
