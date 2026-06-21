use thiserror::Error;

use crate::types::{normalize_optional_string, serialize::{Column, ColumnType}};

#[derive(Debug, Error)]
pub enum ColumnValidationError {
    #[error("WIP limit is invalid.")]
    InvalidWipLimit,
}

// This struct represents the data of a column that is provided by the user.
#[derive(Debug, Clone, PartialEq)]
pub struct UserColumn {
    pub column_type: ColumnType,
    pub wip_limit: String,
}

impl UserColumn {
    pub fn validate(&self) -> Result<Column, ColumnValidationError> {
        let column_type = self.column_type;
        let wip_limit_as_option = normalize_optional_string(self.wip_limit.clone());

        let wip_limit = match wip_limit_as_option {
            Some(limit) => Some(limit.parse().map_err(|_| ColumnValidationError::InvalidWipLimit)?),
            None => None,
        };

        Ok(Column::new(column_type, wip_limit))
    }
}
