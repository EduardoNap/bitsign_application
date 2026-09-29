"""Seed script for dashboard dummy data."""

from __future__ import annotations

import sys
from pathlib import Path

import reflex as rx
from sqlmodel import delete

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bob.models import (  # noqa: E402
    CheckTableItem,
    DailyTraffic,
    DashboardStats,
    MonthlySpending,
    PieChartData,
    WeeklyRevenue,
)


def seed_dashboard() -> None:
    """Replace dashboard content with deterministic dummy data."""
    # Ensure tables exist for first-time local setup.
    rx.Model.create_all()

    with rx.session() as session:
        for model in (
            DashboardStats,
            CheckTableItem,
            DailyTraffic,
            WeeklyRevenue,
            MonthlySpending,
            PieChartData,
        ):
            session.exec(delete(model))

        session.add(
            DashboardStats(
                earnings=4320000.0,
                spend_month=660000.0,
                sales=14.0,
                sales_growth=8.0,
                balance=126000.0,
                tasks=11,
                projects=184,
            )
        )

        session.add_all(
            [
                CheckTableItem(
                    name="Arrendamiento Colima Local 3",
                    progress=88.0,
                    quantity=66000,
                    date_val="31.Ene.2026",
                    checked=False,
                ),
                CheckTableItem(
                    name="Anexo de renta e INPC 2027",
                    progress=72.0,
                    quantity=112000,
                    date_val="01.Feb.2027",
                    checked=True,
                ),
                CheckTableItem(
                    name="Revision clausula de mora (2%)",
                    progress=54.0,
                    quantity=50000,
                    date_val="15.Mar.2026",
                    checked=True,
                ),
                CheckTableItem(
                    name="Verificacion obligado solidario",
                    progress=39.0,
                    quantity=78000,
                    date_val="10.Abr.2026",
                    checked=False,
                ),
            ]
        )

        session.add_all(
            [
                DailyTraffic(day="Lun", visitors=12),
                DailyTraffic(day="Mar", visitors=15),
                DailyTraffic(day="Mie", visitors=11),
                DailyTraffic(day="Jue", visitors=9),
                DailyTraffic(day="Vie", visitors=13),
                DailyTraffic(day="Sab", visitors=6),
                DailyTraffic(day="Dom", visitors=4),
            ]
        )

        session.add_all(
            [
                WeeklyRevenue(day=17, revenue=46),
                WeeklyRevenue(day=18, revenue=52),
                WeeklyRevenue(day=19, revenue=49),
                WeeklyRevenue(day=20, revenue=58),
                WeeklyRevenue(day=21, revenue=63),
                WeeklyRevenue(day=22, revenue=56),
                WeeklyRevenue(day=23, revenue=61),
                WeeklyRevenue(day=24, revenue=67),
                WeeklyRevenue(day=25, revenue=59),
            ]
        )

        session.add_all(
            [
                MonthlySpending(month="SEP", amount=298.0),
                MonthlySpending(month="OCT", amount=304.5),
                MonthlySpending(month="NOV", amount=309.2),
                MonthlySpending(month="DEC", amount=317.8),
                MonthlySpending(month="JAN", amount=323.1),
                MonthlySpending(month="FEB", amount=329.4),
            ]
        )

        session.add_all(
            [
                PieChartData(label="Pago puntual", value=68, color="#422AFB"),
                PieChartData(label="Con mora", value=19, color="#6AD2FF"),
                PieChartData(label="En revision legal", value=13, color="#E5EDFF"),
            ]
        )

        session.commit()


if __name__ == "__main__":
    seed_dashboard()
    print("Seeded dashboard dummy data.")
