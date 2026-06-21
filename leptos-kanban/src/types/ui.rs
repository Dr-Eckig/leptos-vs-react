#[allow(dead_code)]
#[derive(Default, Debug, Clone)]
pub enum Color {
    #[default]
    None,
    Primary,
    Link,
    Info,
    Success,
    Warning,
    Danger,
    White,
    Light,
    Dark,
    Black,
    Text,
    Ghost,
}

impl Color {
    pub fn as_class(&self) -> &'static str {
        match self {
            Self::None => "",
            Self::Primary => "is-primary",
            Self::Link => "is-link",
            Self::Info => "is-info",
            Self::Success => "is-success",
            Self::Warning => "is-warning",
            Self::Danger => "is-danger",
            Self::White => "is-white",
            Self::Light => "is-light",
            Self::Dark => "is-dark",
            Self::Black => "is-black",
            Self::Text => "is-text",
            Self::Ghost => "is-ghost",
        }
    }

    pub fn as_text_color_class(&self) -> &'static str {
        match self {
            Self::None => "",
            Self::Primary => "has-text-primary",
            Self::Link => "has-text-link",
            Self::Info => "has-text-info",
            Self::Success => "has-text-success",
            Self::Warning => "has-text-warning",
            Self::Danger => "has-text-danger",
            Self::White => "has-text-white",
            Self::Light => "has-text-light",
            Self::Dark => "has-text-dark",
            Self::Black => "has-text-black",
            Self::Text => "",
            Self::Ghost => "",
        }
    }
}

#[allow(dead_code)]
#[derive(Default, Debug, Clone)]
pub enum Size {
    Small,
    #[default]
    Normal,
    Medium,
    Large,
}

impl Size {
    pub fn as_class(&self) -> &'static str {
        match self {
            Self::Small => "is-small",
            Self::Normal => "",
            Self::Medium => "is-medium",
            Self::Large => "is-large",
        }
    }
}

#[allow(dead_code)]
#[derive(Default, Debug, Clone)]
pub enum ButtonState {
    #[default]
    Normal,
    Loading,
    Disabled,
}

impl ButtonState {
    pub fn as_class(&self) -> &'static str {
        match self {
            ButtonState::Normal | ButtonState::Disabled => "",
            ButtonState::Loading => "is-loading",
        }
    }
}

#[allow(dead_code)]
#[derive(Default, Debug, Clone)]
pub enum Alignment {
    #[default]
    Left,
    Right,
}

impl Alignment {
    pub fn as_class(&self) -> &'static str {
        match self {
            Alignment::Left => "",
            Alignment::Right => "is-right",
        }
    }
}

#[allow(dead_code)]
#[derive(Default, Debug, Clone)]
pub enum InputType {
    #[default]
    Text,
    Date,
    Email,
    Password,
    Number,
}

impl InputType {
    pub fn as_html_type(&self) -> &'static str {
        match self {
            InputType::Text => "text",
            InputType::Date => "date",
            InputType::Email => "email",
            InputType::Password => "password",
            InputType::Number => "number",
        }
    }
}
