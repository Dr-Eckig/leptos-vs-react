use leptos::{ev, prelude::*};

use crate::types::{
    app_context::AppContext,
    drag_and_drop::{DRAGGABLE_ITEM_MIME_TYPE, DRAGGABLE_ITEM_TEXT_FALLBACK, DraggableItemDto},
};

#[component]
pub fn DraggableItem(
    data: DraggableItemDto,
    #[prop(into, optional)] data_test_id: Signal<String>,
    children: Children,
) -> impl IntoView {
    let app: AppContext = expect_context();
    let is_dragging = RwSignal::new(false);

    let html_class = move || {
        format!(
            "kanban-draggable-item {}",
            if is_dragging.get() { "is-dragging" } else { "" },
        )
    };

    let handle_drag_start = move |event: ev::DragEvent| {
        is_dragging.set(true);
        app.drag_and_drop.dragged_item.set(Some(data));

        if let Some(data_transfer) = event.data_transfer() {
            data_transfer.set_effect_allowed("move");

            if let Some(payload) = data.to_payload() {
                let _ = data_transfer.set_data(DRAGGABLE_ITEM_MIME_TYPE, &payload);
                let _ = data_transfer.set_data(DRAGGABLE_ITEM_TEXT_FALLBACK, &payload);
            }
        }
    };

    let handle_drag_end = move |_| {
        is_dragging.set(false);
        app.drag_and_drop.dragged_item.set(None);
    };

    view! {
        <div
            class=html_class
            draggable="true"
            data-testid=data_test_id
            on:dragstart=handle_drag_start
            on:dragend=handle_drag_end
        >
            { children() }
        </div>
    }
}
