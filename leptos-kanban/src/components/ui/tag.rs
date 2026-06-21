use leptos::prelude::*;

use crate::types::ui::{Color, Size};

#[component]
pub fn Tag(
    #[prop(into)] text: Signal<String>,
    #[prop(into, optional)] color: Signal<Color>,
    #[prop(into, optional)] size: Signal<Size>,
    #[prop(default = false)] is_rounded: bool,
    #[prop(default = false)] is_light: bool,
) -> impl IntoView {
    let tag_class = move || {
        format!(
            "tag {} {} {} {}",
            color.get().as_class(),
            size.get().as_class(),
            if is_rounded { "is-rounded" } else { "" },
            if is_light { "is-light" } else { "" },
        )
    };

    view! {
        <span class=tag_class> { text } </span>
    }
}
