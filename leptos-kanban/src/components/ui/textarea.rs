use leptos::prelude::*;

#[component]
pub fn Textarea(
    #[prop(into)] label: String,
    value: RwSignal<String>,
    #[prop(into, optional)] error_message: Signal<Option<String>>,
    #[prop(into, optional)] placeholder: String,
    #[prop(default = false)] has_fixed_size: bool,
) -> impl IntoView {
    let has_error = move || error_message.with(|error| error.is_some());
    let error_text = move || error_message.with(|error| error.clone().unwrap_or_default());

    view! {
        <div class="field">
            <label class="label"> { label } </label>
            <div class="control">
                <textarea
                    class="textarea"
                    class:has-fixed-size=has_fixed_size
                    class:is-danger=has_error
                    placeholder=placeholder
                    prop:value=value
                    on:input=move |ev| value.set(event_target_value(&ev))
                />
            </div>
            <Show when=has_error>
                 <p class="help is-danger"> { error_text } </p>
            </Show>
        </div>
    }
}
