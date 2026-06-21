use leptos::prelude::*;

use crate::components::ui::icons::FontawesomeIcon;
use crate::types::ui::Color;

#[component]
pub fn IconText(
    icon: FontawesomeIcon,
    #[prop(into)] text: Signal<String>,
    #[prop(optional)] color: Color,
    #[prop(default = false)] text_color: bool,
) -> impl IntoView {
    let icon_text_class = format!(
        "icon-text {}",
        if text_color {
            color.as_text_color_class()
        } else {
            ""
        },
    );

    let icon_class = format!("icon {}", color.as_text_color_class(),);

    view! {
        <div class=icon_text_class>
            <span class=icon_class>
                <i class=icon.as_fontawesome() />
            </span>
            <span> { text } </span>
        </div>
    }
}
