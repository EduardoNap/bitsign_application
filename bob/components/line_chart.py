"""Line chart — contract expirations by month."""

from __future__ import annotations

import reflex as rx

from bob.state import DashboardState


def line_chart() -> rx.Component:
    """Line chart card: vencimientos por mes."""
    return rx.box(
        rx.vstack(
            rx.text(
                "Vencimientos por Mes",
                font_size="16px",
                font_weight="700",
                color="#2B3674",
            ),
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="count",
                    stroke="#422AFB",
                    stroke_width=2,
                    dot=True,
                    type_="monotone",
                ),
                rx.recharts.x_axis(
                    data_key="month",
                    tick_size=10,
                    font_size="11px",
                    angle=-40,
                    text_anchor="end",
                    height=70,
                    padding={"left": 20},
                ),
                rx.recharts.y_axis(
                    font_size="11px",
                    width=40,
                    allow_decimals=False,
                ),
                rx.recharts.tooltip(),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3", opacity=0.3),
                data=DashboardState.line_chart_series,
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