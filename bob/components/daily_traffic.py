"""Daily traffic chart card."""

from __future__ import annotations

import reflex as rx

from bob.state import DashboardState


def daily_traffic() -> rx.Component:
    """Render daily traffic bars and total visitors."""
    return rx.box(
        rx.hstack(
            rx.text("Alertas contractuales diarias", color="#A3AED0", font_size="14px", font_weight="600"),
            rx.hstack(
                rx.icon("trending_up", size=12, color="#05CD99"),
                rx.text("-8.4%", color="#05CD99", font_size="14px", font_weight="700"),
                spacing="1",
                align="center",
            ),
            justify="between",
            width="100%",
        ),
        rx.hstack(
            rx.text(DashboardState.traffic_total_label, font_size="26px", font_weight="800", color="#2B3674"),
            rx.text("Alertas", color="#A3AED0", font_size="14px", font_weight="500", margin_top="6px"),
            spacing="2",
            align="end",
            margin_bottom="8px",
        ),
        rx.recharts.responsive_container(
            rx.recharts.bar_chart(
                rx.recharts.x_axis(
                    data_key="day",
                    axis_line=False,
                    tick_line=False,
                    stroke="#A3AED0",
                    font_size=12,
                ),
                rx.recharts.y_axis(hide=True),
                rx.recharts.tooltip(
                    content_style={
                        "border": "1px solid #E9EDF7",
                        "borderRadius": "12px",
                    }
                ),
                rx.recharts.bar(
                    data_key="visitors",
                    fill="#6A53FA",
                    radius=[10, 10, 0, 0],
                    bar_size=22,
                ),
                data=DashboardState.daily_traffic_chart,
                margin={"top": 5, "right": 0, "left": 0, "bottom": 0},
            ),
            width="100%",
            height=150,
        ),
        width="100%",
        background_color="white",
        border_radius="18px",
        border="1px solid #E9EDF7",
        padding="14px",
        box_shadow="0 8px 24px rgba(67, 24, 255, 0.04)",
    )
