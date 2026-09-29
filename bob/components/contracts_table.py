"""Table — upcoming contract expirations (next 90 days)."""

from __future__ import annotations

import reflex as rx

from bob.state import DashboardState, ContractRow


def _urgency_badge(dias: rx.Var) -> rx.Component:
    """Color-coded badge based on days remaining."""
    return rx.cond(
        dias <= 30,
        rx.box(
            rx.text(
                dias.to(str) + " días",
                font_size="12px",
                font_weight="600",
                color="#E11D48",
            ),
            background="rgba(225, 29, 72, 0.08)",
            padding="2px 10px",
            border_radius="8px",
        ),
        rx.cond(
            dias <= 60,
            rx.box(
                rx.text(
                    dias.to(str) + " días",
                    font_size="12px",
                    font_weight="600",
                    color="#FFB547",
                ),
                background="rgba(255, 181, 71, 0.08)",
                padding="2px 10px",
                border_radius="8px",
            ),
            rx.box(
                rx.text(
                    dias.to(str) + " días",
                    font_size="12px",
                    font_weight="600",
                    color="#01B574",
                ),
                background="rgba(1, 181, 116, 0.08)",
                padding="2px 10px",
                border_radius="8px",
            ),
        ),
    )


def _table_row(contract: ContractRow) -> rx.Component:
    """Single row in the expirations table."""
    return rx.hstack(
        rx.vstack(
            rx.text(
                contract.contract_name,
                font_size="13px",
                font_weight="600",
                color="#2B3674",
                no_of_lines=1,
            ),
            rx.text(
                contract.sucursal,
                font_size="12px",
                color="#A3AED0",
                no_of_lines=1,
            ),
            spacing="0",
            min_width="0",
            flex="1",
        ),
        rx.text(
            contract.estado,
            font_size="12px",
            color="#A3AED0",
            min_width="80px",
            text_align="center",
            display=rx.breakpoints(initial="none", md="block"),
        ),
        rx.text(
            "$" + contract.renta_mensual.to(str),
            font_size="13px",
            font_weight="600",
            color="#2B3674",
            min_width="90px",
            text_align="right",
            display=rx.breakpoints(initial="none", lg="block"),
        ),
        rx.text(
            contract.fecha_vencimiento,
            font_size="12px",
            color="#2B3674",
            min_width="85px",
            text_align="center",
        ),
        _urgency_badge(contract.dias_restantes),
        width="100%",
        padding_y="8px",
        border_bottom="1px solid #F0F2F7",
        align="center",
        spacing="3",
    )


def contracts_table() -> rx.Component:
    """Card: upcoming contract expirations within 90 days."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(
                    "Próximos Vencimientos",
                    font_size="16px",
                    font_weight="700",
                    color="#2B3674",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.box(
                        width="8px", height="8px", border_radius="50%",
                        background="#E11D48",
                    ),
                    rx.text("≤30d", font_size="11px", color="#A3AED0"),
                    rx.box(
                        width="8px", height="8px", border_radius="50%",
                        background="#FFB547",
                    ),
                    rx.text("≤60d", font_size="11px", color="#A3AED0"),
                    rx.box(
                        width="8px", height="8px", border_radius="50%",
                        background="#01B574",
                    ),
                    rx.text("≤90d", font_size="11px", color="#A3AED0"),
                    spacing="2",
                    align="center",
                ),
                width="100%",
                align="center",
            ),
            # Table header
            rx.hstack(
                rx.text(
                    "Contrato",
                    font_size="11px",
                    font_weight="600",
                    color="#A3AED0",
                    text_transform="uppercase",
                    letter_spacing="0.05em",
                    flex="1",
                ),
                rx.text(
                    "Estado",
                    font_size="11px",
                    font_weight="600",
                    color="#A3AED0",
                    text_transform="uppercase",
                    letter_spacing="0.05em",
                    min_width="80px",
                    text_align="center",
                    display=rx.breakpoints(initial="none", md="block"),
                ),
                rx.text(
                    "Renta",
                    font_size="11px",
                    font_weight="600",
                    color="#A3AED0",
                    text_transform="uppercase",
                    letter_spacing="0.05em",
                    min_width="90px",
                    text_align="right",
                    display=rx.breakpoints(initial="none", lg="block"),
                ),
                rx.text(
                    "Vence",
                    font_size="11px",
                    font_weight="600",
                    color="#A3AED0",
                    text_transform="uppercase",
                    letter_spacing="0.05em",
                    min_width="85px",
                    text_align="center",
                ),
                rx.text(
                    "Plazo",
                    font_size="11px",
                    font_weight="600",
                    color="#A3AED0",
                    text_transform="uppercase",
                    letter_spacing="0.05em",
                    min_width="70px",
                    text_align="center",
                ),
                width="100%",
                padding_y="8px",
                border_bottom="2px solid #F0F2F7",
                spacing="3",
            ),
            # Rows
            rx.cond(
                DashboardState.upcoming_contracts.length() > 0,
                rx.vstack(
                    rx.foreach(
                        DashboardState.upcoming_contracts,
                        _table_row,
                    ),
                    spacing="0",
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.icon("check-circle", size=32, color="#01B574"),
                        rx.text(
                            "No hay contratos por vencer en los próximos 90 días",
                            font_size="14px",
                            color="#A3AED0",
                            text_align="center",
                        ),
                        spacing="2",
                        align="center",
                        padding_y="24px",
                    ),
                ),
            ),
            spacing="3",
            width="100%",
        ),
        background="white",
        border_radius="16px",
        padding="20px",
        box_shadow="0 1px 3px rgba(0,0,0,0.04)",
        width="100%",
        max_height="460px",
        overflow_y="auto",
    )