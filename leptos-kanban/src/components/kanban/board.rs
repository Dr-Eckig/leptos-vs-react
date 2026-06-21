use leptos::prelude::*;

use crate::{
    components::{BoardModal, ColumnModal, DownloadLogsButton, Sidebar, TaskColumn, TaskModal},
    types::app_context::AppContext,
};

#[component]
pub fn Board() -> impl IntoView {
    let app: AppContext = expect_context();

    let board_columns = Signal::derive(move || {
        app.boards
            .current_board()
            .map(|board| board.columns.get())
            .unwrap_or_default()
    });

    view! {
        <div class="is-flex">
            <Sidebar />
            <div class="container is-fluid page-height">
                <section class="section is-flex is-flex-direction-column full-height px-0">
                    <div class="is-flex is-justify-content-end pr-3">
                        <DownloadLogsButton />
                    </div>
                    <div class="columns is-flex-grow-1 full-height m-0">
                        <For
                            each=move || board_columns.get()
                            key=|column| column.id
                            children=move |column| {
                                view! {
                                    <TaskColumn column />
                                }
                            }
                        />
                    </div>
                    <BoardModal />
                    <ColumnModal />
                    <TaskModal />
                </section>
            </div>
        </div>
    }
}
