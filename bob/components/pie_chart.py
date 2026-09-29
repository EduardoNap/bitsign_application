"""Pie chart — contracts by state (estado)."""

from __future__ import annotations

import reflex as rx

from bob.state import DashboardState


def pie_chart() -> rx.Component:
    """Pie chart card: contratos por estado."""
    return rx.box(
        rx.vstack(
            rx.text(
                "Contratos por Estado",
                font_size="16px",
                font_weight="700",
                color="#2B3674",
            ),
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    data=DashboardState.pie_chart_series,
                    data_key="value",
                    name_key="label",
                    cx="50%",
                    cy="50%",
                    outer_radius="80%",
                    inner_radius="50%",
                    padding_angle=2,
                    label=True,
                ),
                rx.recharts.tooltip(),
                rx.recharts.legend(
                    icon_size=8,
                    font_size="12px",
                ),
                width="100%",
                height=280,
            ),
            spacing="3",
            width="100%",
        ),
        background="white",
        border_radius="16px",
        padding="20px",
        box_shadow="0 1px 3px rgba(0,0,0,0.04)",
        width="100%",
    )