// @generated automatically by Diesel CLI.

diesel::table! {
    stockpiles (name) {
        name -> Text,
        region -> Text,
        code -> Int4,
    }
}
