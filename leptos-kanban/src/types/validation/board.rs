use thiserror::Error;

use crate::types::serialize::Board;

#[derive(Debug, Error)]
pub enum BoardValidationError {
    #[error("Board title must not be empty.")]
    EmptyTitle,

    #[error("Board title must not be longer than 200 characters.")]
    TitleTooLong,
}

// This struct represents the data of a board that is provided by the user.
#[derive(Debug, Clone, PartialEq)]
pub struct UserBoard {
    pub title: String,
}

impl UserBoard {
    pub fn validate(&self) -> Result<Board, BoardValidationError> {
        let title = validate_title_value(&self.title)?;
        Ok(Board::new(title))
    }
}

fn validate_title_value(title: &str) -> Result<String, BoardValidationError> {
    if title.trim().is_empty() {
        return Err(BoardValidationError::EmptyTitle);
    }

    if title.len() > 200 {
        return Err(BoardValidationError::TitleTooLong);
    }

    Ok(String::from(title.trim()))
}
