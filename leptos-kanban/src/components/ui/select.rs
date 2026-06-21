use leptos::prelude::*;

#[component]
pub fn Select(
    #[prop(into)] label: String,
    options: Vec<String>,
    value: RwSignal<String>,
    #[prop(into, optional)] error_message: Signal<Option<String>>,
) -> impl IntoView {
    let has_error = move || error_message.with(|error| error.is_some());
    let error_text = move || error_message.with(|error| error.clone().unwrap_or_default());

    view! {
        <div class="field">
            <label class="label"> { label } </label>
            <div class="control">
                <div class="select">
                    <select
                        class:is-danger=move || has_error()
                        prop:value=value
                        on:change=move |ev| value.set(event_target_value(&ev))
                    >
                        <For
                            each=move || options.clone()
                            key=|option| option.clone()
                            children=|option| {
                                view! {
                                    <option>{ option }</option>
                                }
                            }
                        />

                    </select>
                </div>
            </div>
            <Show when=has_error>
                 <p class="help is-danger"> { error_text } </p>
            </Show>
        </div>
    }
}
