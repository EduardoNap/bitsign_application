"""Main dashboard page — contract analytics from RDS."""

from __future__ import annotations

import reflex as rx

from bob.components import (
    bar_chart,
    contracts_table,
    line_chart,
    pie_chart,
    sidebar,
    stats_row,
    topbar,
)


def dashboard_page() -> rx.Component:
    """Compose the contracts dashboard."""
    return rx.box(
        sidebar("dashboard"),
        rx.box(
            topbar(),
            # KPI cards row
            stats_row(),
            # Row 1: Line chart (expirations by month) + Bar chart (rent by state)
            rx.grid(
                line_chart(),
                bar_chart(),
                width="100%",
                gap="10px",
                margin_bottom="10px",
                min_width="0",
                grid_template_columns=rx.breakpoints(
                    initial="1fr",
                    xl="1fr 1fr",
                ),
            ),
            # Row 2: Upcoming expirations table + Pie chart (by state)
            rx.grid(
                contracts_table(),
                pie_chart(),
                width="100%",
                gap="10px",
                min_width="0",
                grid_template_columns=rx.breakpoints(
                    initial="1fr",
                    xl="1.6fr 1fr",
                ),
            ),
            margin_left=rx.breakpoints(initial="0px", lg="200px"),
            padding=rx.breakpoints(initial="10px", md="14px", xl="16px"),
            padding_top=rx.breakpoints(initial="8px", md="10px", xl="12px"),
            width=rx.breakpoints(initial="100%", lg="calc(100% - 200px)"),
            max_width="100%",
            min_width="0",
        ),
        width="100%",
        max_width="100vw",
        background_color="#F4F7FE",
        min_height="100vh",
        overflow_x="hidden",
    )