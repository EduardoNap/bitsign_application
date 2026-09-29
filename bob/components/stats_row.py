"""KPI stat cards row for the contracts dashboard."""

from __future__ import annotations

import reflex as rx

from bob.state import DashboardState


def _stat_card(
    label: str,
    value: rx.Var | str,
    icon_name: str,
    icon_bg: str = "rgba(66, 42, 251, 0.08)",
    icon_color: str = "#422AFB",
    subtitle: str | rx.Var = "",
    subtitle_color: str = "#05CD99",
) -> rx.Component:
    """A single KPI card."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.center(
                    rx.icon(icon_name, size=20, color=icon_color),
                    width="40px",
                    height="40px",
                    border_radius="12px",
                    background=icon_bg,
                    flex_shrink="0",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.text(
                        value,
                        font_size="22px",
                        font_weight="700",
                        color="#2B3674",
                        text_align="right",
                        line_height="1",
                    ),
                    rx.cond(
                        subtitle != "",
                        rx.text(
                            subtitle,
                            font_size="12px",
                            font_weight="600",
                            color=subtitle_color,
                        ),
                        rx.fragment(),
                    ),
                    spacing="1",
                    align="end",
                ),
                width="100%",
                align="start",
            ),
            rx.text(
                label,
                font_size="13px",
                font_weight="500",
                color="#A3AED0",
                margin_top="4px",
            ),
            spacing="2",
            width="100%",
        ),
        background="white",
        border_radius="16px",
        padding="16px 18px",
        box_shadow="0 1px 3px rgba(0,0,0,0.04)",
        min_width="0",
    )


def stats_row() -> rx.Component:
    """Top row of KPI cards."""
    return rx.grid(
        _stat_card(
            label="Contratos Totales",
            value=DashboardState.total_contracts.to(str),
            icon_name="file-text",
        ),
        _stat_card(
            label="Contratos Activos",
            value=DashboardState.active_contracts.to(str),
            icon_name="check-circle",
            icon_bg="rgba(1, 181, 116, 0.08)",
            icon_color="#01B574",
        ),
        _stat_card(
            label="Contratos Vencidos",
            value=DashboardState.expired_contracts.to(str),
            icon_name="alert-triangle",
            icon_bg="rgba(225, 29, 72, 0.08)",
            icon_color="#E11D48",
        ),
        _stat_card(
            label="Vencen en 30 días",
            value=DashboardState.expiring_30.to(str),
            icon_name="clock",
            icon_bg="rgba(255, 181, 71, 0.08)",
            icon_color="#FFB547",
        ),
        _stat_card(
            label="Renta Mensual Total",
            value=DashboardState.renta_total_fmt,
            icon_name="dollar-sign",
        ),
        _stat_card(
            label="Renta Promedio",
            value=DashboardState.renta_promedio_fmt,
            icon_name="trending-up",
            icon_bg="rgba(46, 147, 250, 0.08)",
            icon_color="#2E93FA",
        ),
        _stat_card(
            label="Depósito en Garantía",
            value=DashboardState.deposito_total_fmt,
            icon_name="shield",
            icon_bg="rgba(123, 97, 255, 0.08)",
            icon_color="#7B61FF",
        ),
        width="100%",
        gap="10px",
        margin_bottom="10px",
        grid_template_columns=rx.breakpoints(
            initial="1fr 1fr",
            md="repeat(4, minmax(0, 1fr))",
            xl="repeat(7, minmax(0, 1fr))",
        ),
    )