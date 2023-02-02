mod models;
mod schema;

use crate::schema::stockpiles::dsl::*;

use axum::extract::Path;
use axum::{
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use diesel::prelude::*;
use diesel::PgConnection;
use models::*;
use serde::Deserialize;
use tracing::{info, instrument};
use tracing_subscriber::fmt;

use std::env;
use std::net::SocketAddr;

#[derive(Deserialize)]
struct CreateStockpile {
    name: String,
    region: String,
    code: i32,
}

fn establish_connection() -> PgConnection {
    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");

    PgConnection::establish(&database_url).expect("DB Connection Error")
}

#[derive(Deserialize)]
struct DeleteStockpile {
    name: String,
}

#[tokio::main]
async fn main() {
    fmt::init();

    let app = Router::new()
        .route("/", get(root))
        .route("/create_stockpile", post(create_stockpile))
        .route("/stockpile/:stockpile_name", get(get_stockpile))
        .route("/stockpiles", get(list_stockpiles))
        .route("/delete_stockpile", post(delete_stockpile));

    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    info!("Serving on addr {}", addr);
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}

#[instrument]
async fn root() -> &'static str {
    "Root"
}

async fn create_stockpile(Json(payload): Json<CreateStockpile>) -> impl IntoResponse {
    let mut connection = establish_connection();
    diesel::insert_into(stockpiles)
        .values(&vec![(
            name.eq(payload.name),
            region.eq(payload.region),
            code.eq(payload.code),
        )])
        .execute(&mut connection)
        .unwrap();

    (StatusCode::CREATED, "fixme")
}

async fn get_stockpile(Path(stockpile_name): Path<String>) -> impl IntoResponse {
    let mut connection = establish_connection();
    let result = stockpiles
        .filter(name.eq(stockpile_name))
        .load::<Stockpile>(&mut connection)
        .unwrap();

    (StatusCode::OK, Json(result))
}

async fn list_stockpiles() -> impl IntoResponse {
    let mut connection = establish_connection();
    let result = stockpiles.load::<Stockpile>(&mut connection).unwrap();

    (StatusCode::OK, Json(result))
}

async fn delete_stockpile(Json(payload): Json<DeleteStockpile>) -> impl IntoResponse {
    let mut connection = establish_connection();
    diesel::delete(stockpiles.filter(name.eq(payload.name)))
        .execute(&mut connection)
        .unwrap();

    (StatusCode::OK, "fixme")
}
