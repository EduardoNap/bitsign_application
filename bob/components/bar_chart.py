"""Bar chart — monthly rent by state."""

from __future__ import annotations

import reflex as rx

from bob.state import DashboardState


def bar_chart() -> rx.Component:
    """Bar chart card: renta mensual por estado."""
    return rx.box(
        rx.vstack(
            rx.text(
                "Renta Mensual por Estado",
                font_size="16px",
                font_weight="700",
                color="#2B3674",
            ),
            rx.recharts.bar_chart(
                rx.recharts.bar(
                    data_key="renta",
                    fill="#422AFB",
                    radius=[4, 4, 0, 0],
                ),
                rx.recharts.x_axis(
                    data_key="label",
                    tick_size=10,
                    font_size="11px",
                    angle=-40,
                    text_anchor="end",
                    height=80,
                ),
                rx.recharts.y_axis(
                    tick_formatter=rx.Var("(v) => `$${(v/1000).toFixed(0)}k`"),
                    font_size="11px",
                    width=55,
                ),
                rx.recharts.tooltip(
                    formatter=rx.Var("(v) => [`$${Number(v).toLocaleString()}`, 'Renta']"),
                ),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3", opacity=0.3),
                data=DashboardState.bar_chart_series,
                width="100%",
                height=300,
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