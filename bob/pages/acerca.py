"""Simple about page."""

from __future__ import annotations

import reflex as rx

from bob.components.sidebar import sidebar


def acerca_page() -> rx.Component:
    """Render a basic about page."""
    return rx.box(
        sidebar("acerca"),
        rx.box(
            rx.vstack(
                rx.heading("Acerca", size="7", color="#2B3674"),
                rx.text(
                    "Informacion general de la aplicacion.",
                    color="#A3AED0",
                    font_size="14px",
                ),
                rx.box(
                    rx.vstack(
                        rx.text("BitSign Dashboard", color="#2B3674", font_weight="700", font_size="18px"),
                        rx.text(
                            "Esta pagina muestra una descripcion simple del proyecto y sus modulos.",
                            color="#2B3674",
                            font_size="14px",
                        ),
                        rx.text("Version: 1.0.0", color="#A3AED0", font_size="13px"),
                        spacing="2",
                        width="100%",
                        align="start",
                    ),
                    width="100%",
                    max_width="560px",
                    background_color="white",
                    border="1px solid #E9EDF7",
                    border_radius="16px",
                    padding="16px",
                    box_shadow="0 8px 24px rgba(67, 24, 255, 0.04)",
                ),
                width="100%",
                spacing="3",
                align="start",
            ),
            margin_left=rx.breakpoints(initial="0px", lg="200px"),
            width=rx.breakpoints(initial="100%", lg="calc(100% - 200px)"),
            max_width="100%",
            min_width="0",
            padding=rx.breakpoints(initial="10px", md="14px", xl="16px"),
            padding_top=rx.breakpoints(initial="8px", md="10px", xl="12px"),
            min_height="100vh",
        ),
        width="100%",
        max_width="100vw",
        background_color="#F4F7FE",
        min_height="100vh",
        overflow_x="hidden",
    )
