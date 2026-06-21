mod components;
mod app;
mod performance;
mod types;

use leptos::prelude::*;

use crate::app::App;

pub fn main() {
    console_error_panic_hook::set_once();
    performance::init_performance_log_session();
    mount_to_body(App);
}
