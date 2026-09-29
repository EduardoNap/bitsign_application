"""Check table card."""

from __future__ import annotations

import reflex as rx

from bob.state import CheckItem, DashboardState


def check_row(item: CheckItem) -> rx.Component:
    """Single table row."""
    return rx.table.row(
        rx.table.row_header_cell(
            rx.hstack(
                rx.checkbox(
                    checked=item.checked,
                    on_change=lambda checked: DashboardState.toggle_check_item(item.id, checked),
                    color_scheme="indigo",
                ),
                rx.text(item.name, color="#2B3674", font_weight="600", font_size="15px"),
                spacing="2",
                align="center",
            )
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(item.progress_label, color="#2B3674", font_weight="700", font_size="14px"),
                rx.progress(
                    value=item.progress_value,
                    max=100,
                    width="140px",
                    color_scheme="indigo",
                    radius="full",
                    size="2",
                ),
                spacing="1",
                align="start",
            )
        ),
        rx.table.cell(rx.text(item.quantity, color="#2B3674", font_weight="700", font_size="15px")),
        rx.table.cell(rx.text(item.date, color="#2B3674", font_weight="700", font_size="15px")),
    )


def check_table() -> rx.Component:
    """Render check table card."""
    return rx.box(
        rx.hstack(
            rx.heading("Contratos con revision critica", size="5", color="#2B3674", font_weight="700"),
            rx.center(
                rx.icon("ellipsis", size=18, color="#422AFB"),
                width="34px",
                height="34px",
                border_radius="10px",
                background_color="#F4F7FE",
            ),
            justify="between",
            align="center",
            width="100%",
            margin_bottom="8px",
        ),
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell(
                            "CONTRATO", color="#A3AED0", font_size="13px", font_weight="700"
                        ),
                        rx.table.column_header_cell(
                            "AVANCE", color="#A3AED0", font_size="13px", font_weight="700"
                        ),
                        rx.table.column_header_cell(
                            "MONTO", color="#A3AED0", font_size="13px", font_weight="700"
                        ),
                        rx.table.column_header_cell(
                            "VENCIMIENTO", color="#A3AED0", font_size="13px", font_weight="700"
                        ),
                    )
                ),
                rx.table.body(rx.foreach(DashboardState.check_items, check_row)),
                width="100%",
                variant="ghost",
                size="2",
            ),
            width="100%",
            overflow_x="auto",
        ),
        width="100%",
        background_color="white",
        border_radius="18px",
        border="1px solid #E9EDF7",
        padding="14px",
        box_shadow="0 8px 24px rgba(67, 24, 255, 0.04)",
    )
