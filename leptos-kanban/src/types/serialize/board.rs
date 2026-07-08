use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::types::serialize::column::{Column, ColumnType};

pub type BoardId = Uuid;

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Board {
    #[serde(default = "Uuid::new_v4")]
    id: BoardId,
    title: String,
    #[serde(default)]
    columns: Columns,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(transparent)]
pub struct Columns(Vec<Column>);

impl Board {
    pub fn new(title: String) -> Self {
        Self {
            id: Uuid::new_v4(),
            title,
            columns: Columns::default(),
        }
    }

    pub fn id(&self) -> BoardId {
        self.id
    }

    pub fn title(&self) -> &str {
        &self.title
    }

    pub fn columns(&self) -> &Vec<Column> {
        self.columns.as_vec()
    }
}

impl Default for Board {
    fn default() -> Self {
        let board_id = Uuid::new_v4();
        Self {
            id: board_id,
            title: String::from("Kanban Board"),
            columns: Columns::default(),
        }
    }
}

impl Columns {
    pub fn as_vec(&self) -> &Vec<Column> {
        &self.0
    }
}

impl Default for Columns {
    fn default() -> Self {
        Self (
            ColumnType::all()
                .iter()
                .map(|column_type| Column::new(*column_type, None))
                .collect(),
        )
    }
}
