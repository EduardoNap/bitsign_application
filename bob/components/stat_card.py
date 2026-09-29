"""Reusable stat card component."""

from __future__ import annotations

import reflex as rx


def stat_card(
    title: str,
    value: rx.Var | str,
    icon_name: str,
    footer: rx.Component | None = None,
    trailing: rx.Component | None = None,
    icon_bg: str = "#F4F7FE",
    icon_color: str = "#422AFB",
) -> rx.Component:
    """Build a single KPI card."""
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.center(
                    rx.icon(icon_name, size=16, color=icon_color),
                    width="36px",
                    height="36px",
                    border_radius="50%",
                    background_color=icon_bg,
                ),
                rx.vstack(
                    rx.text(title, color="#A3AED0", font_size="11px", font_weight="500", white_space="nowrap"),
                    rx.text(value, color="#2B3674", font_size="20px", font_weight="700", line_height="1.1"),
                    spacing="0",
                    align="start",
                ),
                spacing="2",
                align="center",
            ),
            trailing if trailing is not None else rx.fragment(),
            width="100%",
            justify="between",
            align="start",
        ),
        footer if footer is not None else rx.fragment(),
        width="100%",
        background_color="white",
        border_radius="18px",
        border="1px solid #E9EDF7",
        padding="12px",
        min_height="auto",
        display="flex",
        flex_direction="column",
        justify_content="space-between",
        box_shadow="0 8px 24px rgba(67, 24, 255, 0.04)",
    )
