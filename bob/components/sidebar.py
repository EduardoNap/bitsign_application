"""Left fixed navigation sidebar."""

from __future__ import annotations

import reflex as rx


def nav_item(icon_name: str, label: str, href: str, is_active: bool = False) -> rx.Component:
    """Sidebar navigation item."""
    return rx.link(
        rx.box(
            rx.hstack(
                rx.icon(icon_name, size=18, color="#422AFB" if is_active else "#A3AED0"),
                rx.text(
                    label,
                    font_size="14px",
                    font_weight="700" if is_active else "500",
                    color="#2B3674" if is_active else "#A3AED0",
                ),
                spacing="3",
                align="center",
                width="100%",
                padding_y="10px",
                padding_x="8px",
            ),
            rx.box(
                width="3px",
                height="26px",
                border_radius="99px",
                background_color="#422AFB",
                position="absolute",
                right="-18px",
                top="50%",
                transform="translateY(-50%)",
            )
            if is_active
            else rx.fragment(),
            width="100%",
            position="relative",
        ),
        href=href,
        text_decoration="none",
        width="100%",
    )


def sidebar(active_page: str = "dashboard") -> rx.Component:
    """App sidebar container."""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.hstack(
                    rx.center(
                        rx.icon("hexagon", size=20, color="white"),
                        width="36px",
                        height="36px",
                        border_radius="10px",
                        background="linear-gradient(135deg, #6A53FA, #2E93FA)",
                    ),
                    rx.text("BitSign", font_weight="800", color="#2B3674", font_size="20px"),
                    spacing="3",
                    align="center",
                ),
                width="100%",
                height="90px",
                display="flex",
                align_items="center",
                border_bottom="1px solid #E9EDF7",
                padding_x="20px",
            ),
            rx.vstack(
                rx.vstack(
                    nav_item(
                        "layout_dashboard",
                        "Dashboard",
                        "/dashboard",
                        active_page == "dashboard",
                    ),
                    nav_item("message_square", "Chat", "/chat", active_page == "chat"),
                    nav_item(
                        "upload",
                        "Subir Archivo",
                        "/subir-archivo",
                        active_page == "subir-archivo",
                    ),
                    spacing="4",
                    width="100%",
                ),
                rx.box(flex_grow="1"),
                rx.vstack(
                    nav_item(
                        "circle_help",
                        "Acerca",
                        "/acerca",
                        active_page == "acerca",
                    ),
                    spacing="2",
                    width="100%",
                ),
                width="100%",
                height="100%",
                padding_x="16px",
                padding_top="24px",
                padding_bottom="16px",
                align="stretch",
            ),
            width="100%",
            height="100%",
            align="start",
            spacing="0",
            background_color="white",
        ),
        position="fixed",
        left="0",
        top="0",
        width="200px",
        height="100vh",
        border_right="1px solid #E9EDF7",
        z_index="20",
        background_color="white",
        display=rx.breakpoints(initial="none", lg="block"),
    )
