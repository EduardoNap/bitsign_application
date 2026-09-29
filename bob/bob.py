"""Application entry point."""
from __future__ import annotations
import reflex as rx
from bob.pages.acerca import acerca_page
from bob.pages.chat import chat_page
from bob.pages.dashboard import dashboard_page
from bob.pages.subir_archivo import subir_archivo_page
from bob.state import DashboardState
from bob.chat_state import ChatState
from bob.upload_state import UploadState
import bob.chat_models  # register DB tables for migrations

GLOBAL_STYLE = {
    "font_family": "'DM Sans', sans-serif",
    "background_color": "#F4F7FE",
    "color": "#2B3674",
}
app = rx.App(
    style=GLOBAL_STYLE,
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&display=swap"
    ],
)
app.add_page(
    dashboard_page,
    route="/",
    title="Dashboard de Arrendamientos",
    on_load=DashboardState.load_dashboard,
)
app.add_page(
    dashboard_page,
    route="/dashboard",
    title="Dashboard de Arrendamientos",
    on_load=DashboardState.load_dashboard,
)
app.add_page(
    chat_page,
    route="/chat",
    title="Chat",
    on_load=ChatState.init_session,
)
app.add_page(
    subir_archivo_page,
    route="/subir-archivo",
    title="Subir Archivo",
)
app.add_page(
    acerca_page,
    route="/acerca",
    title="Acerca",
)