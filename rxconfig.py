import os
import reflex as rx

config = rx.Config(
    app_name="bob",
    db_url=os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://localhost:5432/bob_dashboard",
    ),
    api_url=os.getenv("API_URL", "http://localhost:8000"),
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)