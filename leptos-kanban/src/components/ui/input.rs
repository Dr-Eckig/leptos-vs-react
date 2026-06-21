use leptos::prelude::*;

use crate::types::ui::InputType;

#[component]
pub fn Input(
    #[prop(into, optional)] label: Option<String>,
    value: RwSignal<String>,
    #[prop(into, optional)] error_message: Signal<Option<String>>,
    #[prop(optional)] input_type: InputType,
    #[prop(optional)] min: Option<i32>,
    #[prop(into, optional)] placeholder: String,
    #[prop(into, optional)] data_test_id: Signal<String>,
) -> impl IntoView {
    let has_error = move || error_message.with(|error| error.is_some());
    let error_text = move || error_message.with(|error| error.clone().unwrap_or_default());

    let adapted_width = if matches!(input_type, InputType::Date) {
        "width: auto;"
    } else {
        ""
    };

    view! {
        <div class="field">
            <label class="label"> { label } </label>
            <div class="control">
                <input
                    style=adapted_width
                    class="input"
                    class:is-danger=has_error
                    type=input_type.as_html_type()
                    placeholder=placeholder
                    min=min
                    prop:value=value
                    on:input=move |ev| value.set(event_target_value(&ev))
                    data-testid=data_test_id
                />
            </div>
            <Show when=has_error>
                 <p class="help is-danger"> { error_text } </p>
            </Show>
        </div>
    }
}
