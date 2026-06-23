use leptos::{ev, prelude::*};

use crate::types::drag_and_drop::{
    DRAGGABLE_ITEM_MIME_TYPE, DRAGGABLE_ITEM_TEXT_FALLBACK, DraggableItemDto,
};

#[component]
pub fn DropZone(
    #[prop(into, optional)] class: String,
    #[prop(into, optional)] data_test_id: Signal<String>,
    on_drop: Callback<DraggableItemDto>,
    #[prop(default = Signal::from(true))] drop_allowed: Signal<bool>,
    children: Children,
) -> impl IntoView {
    let is_drag_over = RwSignal::new(false);
    let drag_counter = RwSignal::new(0);

    let html_class = move || {
        let is_drag_over = is_drag_over.get();
        let drop_allowed = drop_allowed.get();

        format!(
            "{} kanban-drop-zone {} {}",
            class,
            if is_drag_over { "is-drag-over" } else { "" },
            if is_drag_over && !drop_allowed {
                "disabled-drop"
            } else {
                ""
            },
        )
    };

    let read_dragged_item = |event: &ev::DragEvent| {
        event.data_transfer().and_then(|data_transfer| {
            let payload = data_transfer
                .get_data(DRAGGABLE_ITEM_MIME_TYPE)
                .ok()
                .filter(|payload| !payload.is_empty())
                .or_else(|| {
                    data_transfer
                        .get_data(DRAGGABLE_ITEM_TEXT_FALLBACK)
                        .ok()
                        .filter(|payload| !payload.is_empty())
                });
            payload.and_then(|payload| DraggableItemDto::from_payload(&payload))
        })
    };

    let handle_drag_enter = move |event: ev::DragEvent| {
        event.prevent_default();
        event.stop_propagation();

        drag_counter.update(|counter| *counter += 1);
        is_drag_over.set(true);
    };

    let handle_drag_over = move |event: ev::DragEvent| {
        event.prevent_default();
        event.stop_propagation();

        if let Some(data_transfer) = event.data_transfer() {
            data_transfer.set_drop_effect(if drop_allowed.get() { "move" } else { "none" });
        }
    };

    let handle_drag_leave = move |event: ev::DragEvent| {
        event.prevent_default();
        event.stop_propagation();

        drag_counter.update(|counter| *counter -= 1);
        if drag_counter.get() <= 0 {
            drag_counter.set(0);
            is_drag_over.set(false);
        }
    };

    let handle_drop = move |event: ev::DragEvent| {
        event.prevent_default();
        event.stop_propagation();

        drag_counter.set(0);
        is_drag_over.set(false);

        if let Some(item) = read_dragged_item(&event) {
            if drop_allowed.get() {
                on_drop.run(item);
            }
        }
    };

    view! {
        <div
            class=html_class
            data-testid=data_test_id
            on:dragenter=handle_drag_enter
            on:dragover=handle_drag_over
            on:dragleave=handle_drag_leave
            on:drop=handle_drop
        >
            { children() }
        </div>
    }
}
