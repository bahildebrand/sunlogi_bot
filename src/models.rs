use diesel::prelude::*;
use serde::Serialize;

#[derive(Queryable, Serialize)]
pub struct Stockpile {
    pub name: String,
    pub region: String,
    pub code: i32,
}
