"""Dashboard state — queries the contracts table in RDS PostgreSQL."""

from __future__ import annotations

from datetime import date, timedelta

import reflex as rx
from pydantic import BaseModel
from sqlalchemy import text


# ── Serializable models for the frontend ─────────────────


class ContractRow(BaseModel):
    """A contract row for the upcoming-expirations table."""

    contract_name: str
    sucursal: str
    estado: str
    renta_mensual: float
    fecha_vencimiento: str
    dias_restantes: int


class PieSlice(BaseModel):
    label: str
    value: int
    fill: str


class BarPoint(BaseModel):
    label: str
    renta: float


class LinePoint(BaseModel):
    month: str
    count: int


# Color palette for pie / bar charts
_COLORS = [
    "#422AFB", "#2E93FA", "#01B574", "#FFB547", "#E11D48",
    "#7B61FF", "#38BDF8", "#10B981", "#F59E0B", "#EF4444",
    "#6366F1", "#14B8A6", "#F97316", "#EC4899", "#8B5CF6",
    "#06B6D4", "#84CC16", "#D946EF", "#0EA5E9", "#A855F7",
]


class DashboardState(rx.State):
    """Loads all dashboard KPIs and chart data from the contracts table."""

    # ── KPI cards ────────────────────────────────────────
    total_contracts: int = 0
    active_contracts: int = 0
    expired_contracts: int = 0
    expiring_30: int = 0
    expiring_60: int = 0
    expiring_90: int = 0
    renta_total: float = 0.0
    renta_promedio: float = 0.0
    deposito_total: float = 0.0

    # ── Chart data ───────────────────────────────────────
    pie_data: list[PieSlice] = []
    bar_data: list[BarPoint] = []
    line_data: list[LinePoint] = []
    upcoming_contracts: list[ContractRow] = []

    def load_dashboard(self) -> None:
        """Fetch all dashboard data from the contracts table."""
        today = date.today()
        d30 = today + timedelta(days=30)
        d60 = today + timedelta(days=60)
        d90 = today + timedelta(days=90)

        try:
            with rx.session() as session:
                # ── KPIs ─────────────────────────────────
                row = session.execute(
                    text("""
                        SELECT
                            COUNT(*)                                                       AS total,
                            COUNT(*) FILTER (WHERE fecha_vencimiento >= :today)             AS active,
                            COUNT(*) FILTER (WHERE fecha_vencimiento <  :today)             AS expired,
                            COUNT(*) FILTER (WHERE fecha_vencimiento BETWEEN :today AND :d30) AS exp30,
                            COUNT(*) FILTER (WHERE fecha_vencimiento BETWEEN :today AND :d60) AS exp60,
                            COUNT(*) FILTER (WHERE fecha_vencimiento BETWEEN :today AND :d90) AS exp90,
                            COALESCE(SUM(renta_mensual), 0)                                AS renta_sum,
                            COALESCE(AVG(renta_mensual), 0)                                AS renta_avg,
                            COALESCE(SUM(deposito_garantia), 0)                            AS dep_sum
                        FROM contracts
                    """),
                    {"today": today, "d30": d30, "d60": d60, "d90": d90},
                ).fetchone()

                if row:
                    self.total_contracts = row.total or 0
                    self.active_contracts = row.active or 0
                    self.expired_contracts = row.expired or 0
                    self.expiring_30 = row.exp30 or 0
                    self.expiring_60 = row.exp60 or 0
                    self.expiring_90 = row.exp90 or 0
                    self.renta_total = float(row.renta_sum or 0)
                    self.renta_promedio = float(row.renta_avg or 0)
                    self.deposito_total = float(row.dep_sum or 0)

                # ── Pie: contratos por estado ────────────
                pie_rows = session.execute(
                    text("""
                        SELECT COALESCE(estado, 'Sin estado') AS estado, COUNT(*) AS cnt
                        FROM contracts
                        GROUP BY estado
                        ORDER BY cnt DESC
                    """)
                ).fetchall()

                self.pie_data = [
                    PieSlice(
                        label=r.estado,
                        value=r.cnt,
                        fill=_COLORS[i % len(_COLORS)],
                    )
                    for i, r in enumerate(pie_rows)
                ]

                # ── Bar: renta total por estado ──────────
                bar_rows = session.execute(
                    text("""
                        SELECT COALESCE(estado, 'Sin estado') AS estado,
                               COALESCE(SUM(renta_mensual), 0) AS renta
                        FROM contracts
                        GROUP BY estado
                        ORDER BY renta DESC
                        LIMIT 12
                    """)
                ).fetchall()

                self.bar_data = [
                    BarPoint(label=r.estado, renta=float(r.renta))
                    for r in bar_rows
                ]

                # ── Line: vencimientos por mes ───────────
                line_rows = session.execute(
                    text("""
                        SELECT TO_CHAR(fecha_vencimiento, 'YYYY-MM') AS month,
                               COUNT(*) AS cnt
                        FROM contracts
                        WHERE fecha_vencimiento IS NOT NULL
                        GROUP BY month
                        ORDER BY month
                    """)
                ).fetchall()

                self.line_data = [
                    LinePoint(month=r.month, count=r.cnt) for r in line_rows
                ]

                # ── Table: próximos por vencer (90 días) ─
                table_rows = session.execute(
                    text("""
                        SELECT contract_name,
                               COALESCE(sucursal_vertiche, '-') AS sucursal,
                               COALESCE(estado, '-') AS estado,
                               COALESCE(renta_mensual, 0) AS renta_mensual,
                               fecha_vencimiento,
                               (fecha_vencimiento - :today) AS dias
                        FROM contracts
                        WHERE fecha_vencimiento BETWEEN :today AND :d90
                        ORDER BY fecha_vencimiento ASC
                        LIMIT 20
                    """),
                    {"today": today, "d90": d90},
                ).fetchall()

                self.upcoming_contracts = [
                    ContractRow(
                        contract_name=r.contract_name,
                        sucursal=r.sucursal,
                        estado=r.estado,
                        renta_mensual=float(r.renta_mensual),
                        fecha_vencimiento=r.fecha_vencimiento.strftime("%d/%m/%Y")
                        if r.fecha_vencimiento
                        else "-",
                        dias_restantes=r.dias if r.dias else 0,
                    )
                    for r in table_rows
                ]

        except Exception as exc:
            print(f"[DashboardState] Error loading dashboard: {exc}")

    # ── Computed vars for formatting ─────────────────────

    @rx.var
    def renta_total_fmt(self) -> str:
        return f"${self.renta_total:,.0f}"

    @rx.var
    def renta_promedio_fmt(self) -> str:
        return f"${self.renta_promedio:,.0f}"

    @rx.var
    def deposito_total_fmt(self) -> str:
        return f"${self.deposito_total:,.0f}"

    @rx.var
    def pie_chart_series(self) -> list[dict]:
        return [
            {"label": s.label, "value": s.value, "fill": s.fill}
            for s in self.pie_data
        ]

    @rx.var
    def bar_chart_series(self) -> list[dict]:
        return [
            {
                "label": "CDMX" if p.label == "Ciudad de México" else p.label,
                "renta": p.renta,
            }
            for p in self.bar_data
        ]

    @rx.var
    def line_chart_series(self) -> list[dict]:
        return [{"month": p.month, "count": p.count} for p in self.line_data]