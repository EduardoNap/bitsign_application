"""Top navigation bar for the dashboard."""

from __future__ import annotations

import reflex as rx


def topbar() -> rx.Component:
    """Breadcrumb + page title bar."""
    return rx.hstack(
        rx.vstack(
            rx.hstack(
                rx.text("Páginas", font_size="12px", color="#A3AED0"),
                rx.text("/", font_size="12px", color="#A3AED0"),
                rx.text("Dashboard", font_size="12px", color="#A3AED0"),
                spacing="1",
            ),
            rx.text(
                "Dashboard de Contratos",
                font_size="22px",
                font_weight="700",
                color="#2B3674",
                line_height="1.2",
            ),
            spacing="1",
            align="start",
        ),
        rx.spacer(),
        rx.hstack(
            rx.link(
                rx.center(
                    rx.icon("message-square", size=16, color="#422AFB"),
                    width="34px",
                    height="34px",
                    border_radius="10px",
                    background="rgba(66, 42, 251, 0.08)",
                ),
                href="/chat",
            ),
            rx.link(
                rx.center(
                    rx.icon("upload", size=16, color="#422AFB"),
                    width="34px",
                    height="34px",
                    border_radius="10px",
                    background="rgba(66, 42, 251, 0.08)",
                ),
                href="/subir-archivo",
            ),
            spacing="2",
        ),
        width="100%",
        padding_bottom="10px",
        align="end",
    )