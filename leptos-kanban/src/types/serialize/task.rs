use std::{fmt, str::FromStr};

use serde::{Deserialize, Serialize};
use time::Date;
use uuid::Uuid;

pub type TaskId = Uuid;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Task {
    #[serde(default = "Uuid::new_v4")]
    id: TaskId,
    title: String,
    description: Option<String>,
    due_date: Option<Date>,
    priority: Priority,
}

#[derive(Default, Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum Priority {
    Low,
    #[default]
    Medium,
    High,
}

impl Task {
    pub fn with_id(
        id: TaskId,
        title: String,
        description: Option<String>,
        due_date: Option<Date>,
        priority: Priority,
    ) -> Self {
        Task { id, title, description, due_date, priority }
    }

    pub fn new(
        title: String,
        description: Option<String>,
        due_date: Option<Date>,
        priority: Priority,
    ) -> Self {
        Self::with_id(Uuid::new_v4(), title, description, due_date, priority)
    }

    pub fn id(&self) -> TaskId {
        self.id
    }

    pub fn title(&self) -> &str {
        &self.title
    }

    pub fn description(&self) -> Option<&String> {
        self.description.as_ref()
    }

    pub fn due_date(&self) -> Option<&Date> {
        self.due_date.as_ref()
    }

    pub fn priority(&self) -> &Priority {
        &self.priority
    }
}

impl Priority {
    const fn as_str(&self) -> &'static str {
        match self {
            Priority::Low => "Low",
            Priority::Medium => "Medium",
            Priority::High => "High",
        }
    }
}

impl fmt::Display for Priority {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

impl FromStr for Priority {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "low" => Ok(Priority::Low),
            "medium" => Ok(Priority::Medium),
            "high" => Ok(Priority::High),
            _ => Err(()),
        }
    }
}
