#[allow(dead_code)]
#[derive(Clone, Copy)]
pub enum FontawesomeIcon {
    CirclePlus,
    Download,
    Edit,
    Ellipsis,
    EllipsisVertical,
    Plus,
    Trash,
    Reset,
}

impl FontawesomeIcon {
    pub fn as_fontawesome(&self) -> &'static str {
        match self {
            FontawesomeIcon::CirclePlus => "fa-solid fa-circle-plus",
            FontawesomeIcon::Download => "fa-solid fa-circle-down",
            FontawesomeIcon::Edit => "fa-solid fa-pen",
            FontawesomeIcon::Ellipsis => "fa-solid fa-ellipsis",
            FontawesomeIcon::EllipsisVertical => "fa-solid fa-ellipsis-vertical",
            FontawesomeIcon::Plus => "fa-solid fa-plus",
            FontawesomeIcon::Trash => "fa-solid fa-trash-can",
            FontawesomeIcon::Reset => "fa-solid fa-arrow-rotate-left",
        }
    }
}
