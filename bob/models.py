"""Database models for the dashboard."""

from __future__ import annotations

import reflex as rx
from sqlmodel import Field


class DashboardStats(rx.Model, table=True):
    """Top-level KPI values shown in the stat cards."""

    id: int | None = Field(default=None, primary_key=True)
    earnings: float
    spend_month: float
    sales: float
    sales_growth: float
    balance: float
    tasks: int
    projects: int


class CheckTableItem(rx.Model, table=True):
    """Rows used in the check table card."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    progress: float
    quantity: int
    date_val: str
    checked: bool = False


class DailyTraffic(rx.Model, table=True):
    """Daily traffic bars."""

    id: int | None = Field(default=None, primary_key=True)
    day: str
    visitors: int


class WeeklyRevenue(rx.Model, table=True):
    """Weekly revenue chart data."""

    id: int | None = Field(default=None, primary_key=True)
    day: int
    revenue: float


class MonthlySpending(rx.Model, table=True):
    """Monthly line chart data."""

    id: int | None = Field(default=None, primary_key=True)
    month: str
    amount: float


class PieChartData(rx.Model, table=True):
    """Pie chart segments."""

    id: int | None = Field(default=None, primary_key=True)
    label: str
    value: float
    color: str
