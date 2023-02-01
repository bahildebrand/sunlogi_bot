use axum::extract::Path;
use axum::{
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::Deserialize;
use tracing::{info, instrument};
use tracing_subscriber::fmt;

use std::net::SocketAddr;

#[derive(Deserialize)]
struct CreateStockpile {
    name: String,
    Region: String,
    code: u64,
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
        .route("/stockpile/:name", get(get_stockpile))
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
    (StatusCode::CREATED, "fixme")
}

async fn get_stockpile(Path(name): Path<String>) -> impl IntoResponse {
    (StatusCode::OK, "fixme")
}

async fn list_stockpiles() -> impl IntoResponse {
    (StatusCode::OK, "fixme")
}

async fn delete_stockpile(Json(payload): Json<DeleteStockpile>) -> impl IntoResponse {
    (StatusCode::OK, "fixme")
}
