use time::{Date, macros::format_description};

pub mod app_context;
pub mod drag_and_drop;
pub mod modals;
pub mod serialize;
pub mod state;
pub mod ui;
pub mod validation;

pub fn normalize_optional_string(value: String) -> Option<String> {
    let trimmed = value.trim();

    if trimmed.is_empty() {
        None
    } else {
        Some(trimmed.to_string())
    }
}

pub fn format_date_to_display(date: &Date) -> String {
    let format = format_description!("[day].[month].[year]");

    date.format(&format).expect("Failed to format date")
}

pub fn format_date_to_string(date: &Date) -> String {
    let format = format_description!("[year]-[month]-[day]");

    date.format(&format).expect("Failed to format date")
}

pub fn parse_date_from_string(input: &str) -> Result<Date, time::error::Parse> {
    let format = format_description!("[year]-[month]-[day]");

    Date::parse(input, &format)
}
