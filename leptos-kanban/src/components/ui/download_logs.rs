use leptos::prelude::*;
use wasm_bindgen::JsCast;
use web_sys::{HtmlAnchorElement, js_sys::Array};

use crate::{components::{Button, icons::FontawesomeIcon}, performance::{performance_log_file_content, performance_log_file_name}, types::ui::Color};

#[component]
pub fn DownloadLogsButton() -> impl IntoView {
    let on_click = move || {
        let content = performance_log_file_content();
        let filename = performance_log_file_name();

        download_file(content, &filename);
    };

    view! {
        <Button 
            text="Download Logs"
            color=Color::Light
            icon=FontawesomeIcon::Download
            aria_label="Download performance logs as JSON file"
            data_test_id="download-logs-button"
            on_click=on_click
        />
        
    }
}

pub fn download_file(content: String, filename: &str) {
    let blob_parts = Array::new();
    blob_parts.push(&content.into());
    let blob = web_sys::Blob::new_with_str_sequence(&blob_parts).unwrap();

    let url = web_sys::Url::create_object_url_with_blob(&blob).unwrap();

    let document = window().document().unwrap();
    let a: HtmlAnchorElement = document.create_element("a").unwrap().dyn_into().unwrap();

    a.set_href(&url);
    a.set_download(filename);
    a.click();

    web_sys::Url::revoke_object_url(&url).unwrap();
}