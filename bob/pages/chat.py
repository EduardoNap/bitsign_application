"""Chat page with conversation history panel."""

from __future__ import annotations

import reflex as rx

from bob.chat_state import ChatState, ChatMessage, ChatSource, ConversationSummary
from bob.components.sidebar import sidebar


def _suggestion_card(text: str, icon_name: str, icon_bg: str) -> rx.Component:
    """Single suggestion card with icon — 2x2 grid style."""
    return rx.hstack(
        rx.center(
            rx.icon(icon_name, size=20, color=icon_bg),
            width="40px",
            height="40px",
            border_radius="12px",
            background=f"{icon_bg}18",
            flex_shrink="0",
        ),
        rx.text(
            text,
            color="#2B3674",
            font_size="14px",
            font_weight="600",
            line_height="1.3",
            no_of_lines=2,
        ),
        rx.spacer(),
        rx.icon("plus", size=16, color="#A3AED0"),
        width="100%",
        padding="14px 16px",
        border_radius="14px",
        border="1px solid #E9EDF7",
        background="white",
        align="center",
        spacing="3",
        cursor="pointer",
        _hover={"border_color": "#422AFB", "box_shadow": "0 2px 8px rgba(66, 42, 251, 0.08)"},
        transition="all 0.15s ease",
        on_click=ChatState.use_suggestion(text),
    )


def _source_card(source: ChatSource) -> rx.Component:
    """Square source card for Bedrock citation references."""
    return rx.box(
        rx.vstack(
            rx.text(
                source.title,
                font_size="12px",
                font_weight="700",
                color="#2B3674",
                no_of_lines=1,
            ),
            rx.text(
                "Click para ver texto completo",
                font_size="11px",
                color="#A3AED0",
                no_of_lines=1,
            ),
            rx.cond(
                source.snippet != "",
                rx.text(
                    source.snippet,
                    font_size="12px",
                    color="#4A5568",
                    line_height="1.4",
                    no_of_lines=4,
                ),
                rx.fragment(),
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        on_click=ChatState.open_source_preview(
            source.title,
            source.location,
            source.full_text,
        ),
        width="100%",
        min_height="120px",
        padding="10px",
        border="1px solid #E9EDF7",
        border_radius="12px",
        background="#F8FAFD",
        cursor="pointer",
        _hover={"border_color": "#B8C5E6", "background": "#F4F7FE"},
        transition="all 0.15s ease",
    )


def _source_preview_modal() -> rx.Component:
    """Modal with full source text."""
    return rx.cond(
        ChatState.show_source_preview,
        rx.box(
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text(
                                ChatState.source_preview_title,
                                font_size="16px",
                                font_weight="700",
                                color="#2B3674",
                            ),
                            rx.text(
                                ChatState.source_preview_location,
                                font_size="12px",
                                color="#A3AED0",
                                no_of_lines=1,
                            ),
                            spacing="1",
                            align="start",
                            width="100%",
                            min_width="0",
                        ),
                        rx.button(
                            rx.icon("x", size=16),
                            on_click=ChatState.close_source_preview,
                            variant="ghost",
                            cursor="pointer",
                            flex_shrink="0",
                        ),
                        width="100%",
                        align="start",
                        spacing="3",
                    ),
                    rx.box(
                        rx.text(
                            ChatState.source_preview_text,
                            white_space="pre-wrap",
                            color="#2D252C",
                            font_size="14px",
                            line_height="1.55",
                        ),
                        width="100%",
                        max_height=rx.breakpoints(initial="56vh", md="62vh"),
                        overflow_y="auto",
                        padding="14px",
                        border="1px solid #E9EDF7",
                        border_radius="12px",
                        background="#F8FAFD",
                    ),
                    spacing="3",
                    width="100%",
                ),
                width=rx.breakpoints(initial="92vw", md="760px"),
                max_width="92vw",
                padding="16px",
                border_radius="16px",
                background="white",
                box_shadow="0 18px 48px rgba(0, 0, 0, 0.2)",
            ),
            position="fixed",
            inset="0",
            z_index="100",
            background="rgba(17, 24, 39, 0.45)",
            display="flex",
            align_items="center",
            justify_content="center",
            padding="12px",
        ),
        rx.fragment(),
    )


def _message_bubble(message: ChatMessage) -> rx.Component:
    """Render a single chat message bubble."""
    return rx.cond(
        message.is_user,
        rx.box(
            rx.text(
                message.text,
                color="white",
                font_size=rx.breakpoints(initial="14px", md="16px"),
                line_height="1.5",
            ),
            background="linear-gradient(135deg, #6A53FA, #422AFB)",
            padding="12px 16px",
            border_radius="16px 16px 4px 16px",
            max_width="75%",
            margin_left="auto",
            box_shadow="0 2px 8px rgba(66, 42, 251, 0.18)",
        ),
        rx.box(
            rx.hstack(
                rx.center(
                    rx.icon("sparkles", size=14, color="#422AFB"),
                    width="28px",
                    height="28px",
                    border_radius="8px",
                    background="rgba(66, 42, 251, 0.08)",
                    flex_shrink="0",
                ),
                rx.vstack(
                    rx.markdown(
                        message.text,
                        use_raw=False,
                        use_math=False,
                        use_katex=False,
                        color="#2D252C",
                        font_size=rx.breakpoints(initial="14px", md="16px"),
                        line_height="1.6",
                        font_family="inherit",
                        width="100%",
                        style={
                            "& p": {"margin": "0 0 10px 0"},
                            "& p:last-child": {"marginBottom": "0"},
                            "& ul, & ol": {"margin": "0 0 10px 20px", "padding": "0"},
                            "& li": {"marginBottom": "6px"},
                        },
                    ),
                    rx.cond(
                        message.sources.length() > 0,
                        rx.vstack(
                            rx.text(
                                "Fuentes",
                                font_size="11px",
                                font_weight="700",
                                color="#A3AED0",
                                text_transform="uppercase",
                                letter_spacing="0.06em",
                            ),
                            rx.grid(
                                rx.foreach(message.sources, _source_card),
                                columns=rx.breakpoints(initial="1", md="2"),
                                spacing="2",
                                width="100%",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                    min_width="0",
                ),
                align_items="start",
                spacing="3",
                width="100%",
            ),
            background="white",
            padding="14px 16px",
            border_radius="16px 16px 16px 4px",
            max_width="85%",
            box_shadow="0 1px 4px rgba(0, 0, 0, 0.06)",
        ),
    )


def _loading_indicator() -> rx.Component:
    """Typing indicator while the agent is thinking."""
    return rx.box(
        rx.hstack(
            rx.center(
                rx.icon("sparkles", size=14, color="#422AFB"),
                width="28px",
                height="28px",
                border_radius="8px",
                background="rgba(66, 42, 251, 0.08)",
            ),
            rx.hstack(
                rx.box(
                    width="8px", height="8px", border_radius="50%",
                    background="#A3AED0",
                    animation="pulse 1.2s ease-in-out infinite",
                ),
                rx.box(
                    width="8px", height="8px", border_radius="50%",
                    background="#A3AED0",
                    animation="pulse 1.2s ease-in-out 0.2s infinite",
                ),
                rx.box(
                    width="8px", height="8px", border_radius="50%",
                    background="#A3AED0",
                    animation="pulse 1.2s ease-in-out 0.4s infinite",
                ),
                spacing="1",
                align_items="center",
            ),
            spacing="3",
            align_items="center",
        ),
        background="white",
        padding="14px 16px",
        border_radius="16px 16px 16px 4px",
        max_width="120px",
        box_shadow="0 1px 4px rgba(0, 0, 0, 0.06)",
    )


def _conversation_item(conv: ConversationSummary) -> rx.Component:
    """A single conversation row in the history sidebar."""
    return rx.hstack(
        rx.box(
            rx.vstack(
                rx.text(
                    conv.title,
                    font_size="13px",
                    font_weight="600",
                    color="#2B3674",
                    no_of_lines=1,
                    line_height="1.3",
                ),
                rx.text(
                    conv.date_label,
                    font_size="11px",
                    color="#A3AED0",
                ),
                spacing="1",
            ),
            flex="1",
            min_width="0",
            cursor="pointer",
            on_click=ChatState.load_conversation(conv.id),
        ),
        rx.button(
            rx.icon("trash-2", size=13, color="#A3AED0"),
            on_click=ChatState.delete_conversation(conv.id),
            variant="ghost",
            size="1",
            padding="4px",
            cursor="pointer",
            flex_shrink="0",
            _hover={"background": "rgba(225, 29, 72, 0.08)"},
        ),
        width="100%",
        padding="10px 12px",
        border_radius="10px",
        border="1px solid #F0F2F7",
        align="center",
        spacing="2",
        _hover={"background": "rgba(66, 42, 251, 0.04)", "border_color": "#E0E5F2"},
        transition="all 0.15s ease",
    )


def _history_sidebar_content() -> rx.Component:
    """Inner content for the history sidebar."""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.text(
                "Historial",
                font_size="16px",
                font_weight="700",
                color="#2B3674",
            ),
            rx.spacer(),
            # Close button only visible on mobile
            rx.button(
                rx.icon("x", size=16, color="#A3AED0"),
                on_click=ChatState.toggle_history,
                variant="ghost",
                size="1",
                cursor="pointer",
                display=rx.breakpoints(initial="flex", md="none"),
            ),
            width="100%",
            align="center",
        ),
        # New conversation button
        rx.button(
            rx.hstack(
                rx.icon("plus", size=14),
                rx.text("Nueva conversación", font_size="13px"),
                spacing="2",
                align="center",
            ),
            on_click=ChatState.clear_chat,
            width="100%",
            variant="outline",
            color="#422AFB",
            border_color="#E9EDF7",
            border_radius="10px",
            cursor="pointer",
            _hover={"background": "rgba(66, 42, 251, 0.05)"},
        ),
        # Conversation list
        rx.cond(
            ChatState.conversations.length() > 0,
            rx.box(
                rx.vstack(
                    rx.foreach(
                        ChatState.conversations, _conversation_item
                    ),
                    spacing="2",
                    width="100%",
                ),
                flex="1",
                overflow_y="auto",
                width="100%",
            ),
            rx.center(
                rx.text(
                    "No hay conversaciones aún",
                    font_size="13px",
                    color="#A3AED0",
                ),
                padding_y="32px",
            ),
        ),
        spacing="3",
        width="100%",
        height="100%",
        padding="20px 16px",
    )


def _input_hstack() -> rx.Component:
    """Shared input row."""
    return rx.hstack(
        rx.input(
            placeholder="Pregunta algo acerca de tus contratos",
            value=ChatState.current_input,
            on_change=ChatState.set_input,
            on_key_down=ChatState.handle_key_down,
            width="100%",
            border="none",
            background_color="white",
            color="#000000",
            font_family="'DM Sans', sans-serif",
            font_size=rx.breakpoints(initial="14px", md="16px"),
            font_weight="500",
            line_height="1.5",
            padding="0",
            disabled=ChatState.is_loading,
            _placeholder={
                "color": "#000000",
                "font_family": "'DM Sans', sans-serif",
                "font_size": "inherit",
                "opacity": "1",
            },
            style={
                "&::placeholder": {
                    "color": "#000000",
                    "fontFamily": "'DM Sans', sans-serif",
                    "fontSize": "inherit",
                    "opacity": "1",
                },
                "&::-webkit-input-placeholder": {
                    "color": "#000000",
                    "opacity": "1",
                }
            },
            focus_border_color="transparent",
        ),
        rx.button(
            rx.cond(
                ChatState.is_loading,
                rx.spinner(size="2"),
                rx.icon(
                    "send",
                    size=22,
                    color=rx.cond(
                        ChatState.current_input != "",
                        "#422AFB",
                        "#A8A7AA",
                    ),
                    stroke_width=1.8,
                ),
            ),
            on_click=ChatState.send_message,
            disabled=ChatState.is_loading,
            background_color="transparent",
            border="none",
            padding="0",
            min_width="auto",
            cursor=rx.cond(
                ChatState.current_input != "",
                "pointer",
                "default",
            ),
            _hover={"background_color": "transparent"},
        ),
        width="100%",
        border="1px solid #E9EDF7",
        border_radius="16px",
        height=rx.breakpoints(initial="52px", md="56px"),
        align="center",
        padding_x=rx.breakpoints(initial="12px", md="16px"),
        padding_y="0",
        background="white",
        box_shadow="0 2px 12px rgba(0, 0, 0, 0.04)",
    )


def _landing_content() -> rx.Component:
    """The initial landing view — welcome + cards centered, input at very bottom."""
    return rx.vstack(
        rx.box(flex="1"),
        # Welcome section
        rx.vstack(
            rx.text(
                "Bienvenido a",
                color="#A3AED0",
                font_size=rx.breakpoints(initial="16px", md="20px"),
                font_weight="500",
            ),
            rx.text(
                "Consulta de Contratos",
                color="#2B3674",
                font_size=rx.breakpoints(initial="28px", md="52px"),
                font_weight="700",
                line_height="1.1",
            ),
            rx.text(
                "Pregunta lo que sea a nuestra IA sobre tus contratos.",
                color="#A3AED0",
                font_size=rx.breakpoints(initial="14px", md="16px"),
                margin_top="12px",
            ),
            spacing="1",
            align="center",
            text_align="center",
        ),
        # 2x2 suggestion grid
        rx.grid(
            _suggestion_card(
                "¿Cuál es la fecha de vencimiento de este contrato?",
                "calendar",
                "#F6AD55",
            ),
            _suggestion_card(
                "¿Qué cláusulas de penalización incluye este contrato?",
                "shield-alert",
                "#7C5CFC",
            ),
            _suggestion_card(
                "¿Cuál es el monto total y calendario de pagos del contrato?",
                "wallet",
                "#68D391",
            ),
            _suggestion_card(
                "Resume los puntos clave de este contrato",
                "file-text",
                "#FC8181",
            ),
            columns=rx.breakpoints(initial="1", md="2"),
            spacing="3",
            width="100%",
            max_width="680px",
        ),
        rx.box(flex="5"),
        # Input bar at the very bottom
        rx.box(
            _input_hstack(),
            max_width="680px",
            width="100%",
            margin_bottom=rx.breakpoints(initial="20px", md="32px"),
        ),
        spacing="7",
        align="center",
        width="100%",
        height="100%",
        padding_x=rx.breakpoints(initial="14px", md="44px", lg="58px"),
    )


def _chat_messages() -> rx.Component:
    """The conversation view once messages exist."""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.hstack(
                    rx.icon("sparkles", size=20, color="#422AFB", stroke_width=1.8),
                    rx.text(
                        "Consulta de Contratos",
                        color="#2B3674",
                        font_size="18px",
                        font_weight="700",
                    ),
                    spacing="2",
                    align="center",
                ),
                width="100%",
                padding_x=rx.breakpoints(initial="16px", md="32px"),
                padding_top="20px",
                padding_bottom="12px",
            ),
            # Messages area (scrollable)
            rx.auto_scroll(
                rx.vstack(
                    rx.foreach(ChatState.messages, _message_bubble),
                    rx.cond(ChatState.is_loading, _loading_indicator()),
                    spacing="3",
                    width="100%",
                    padding_x=rx.breakpoints(initial="16px", md="32px"),
                    padding_bottom="100px",
                ),
                flex="1",
                min_height="0",
                width="100%",
                style={"scroll_behavior": "smooth"},
            ),
            width="100%",
            height="100%",
            min_height="0",
            spacing="0",
        ),
        # Input bar pinned at bottom
        rx.box(
            _input_hstack(),
            position="absolute",
            bottom=rx.breakpoints(initial="20px", md="26px", lg="30px"),
            left="50%",
            transform="translateX(-50%)",
            width=rx.breakpoints(initial="calc(100% - 28px)", md="calc(100% - 80px)"),
            max_width="680px",
            z_index="3",
        ),
        width="100%",
        height="100%",
        overflow="hidden",
        position="relative",
    )


def chat_page() -> rx.Component:
    """Render the chat page — main content left, history sidebar right."""
    return rx.box(
        # Pulse animation for loading dots
        rx.el.style(
            """
            @keyframes pulse {
                0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
                40% { transform: scale(1); opacity: 1; }
            }
            """
        ),
        sidebar("chat"),
        rx.box(
            # Outer card
            rx.box(
                # Main content area (left)
                rx.box(
                    rx.cond(
                        ChatState.show_landing,
                        _landing_content(),
                        _chat_messages(),
                    ),
                    flex="1",
                    min_width="0",
                    min_height="0",
                    position="relative",
                    overflow="hidden",
                ),
                # History sidebar (right) with full-height left border as divider
                rx.box(
                    _history_sidebar_content(),
                    width=rx.breakpoints(initial="0px", md="300px"),
                    min_width=rx.breakpoints(initial="0px", md="300px"),
                    min_height="0",
                    overflow_y="auto",
                    display=rx.breakpoints(initial="none", md="flex"),
                    flex_direction="column",
                    border_left="1.5px solid #E9EDF7",
                ),
                # Mobile overlay sidebar
                rx.cond(
                    ChatState.show_history,
                    rx.box(
                        _history_sidebar_content(),
                        position="absolute",
                        right="0",
                        top="0",
                        width="280px",
                        height="100%",
                        background="white",
                        border_left="1px solid #E9EDF7",
                        z_index="5",
                        box_shadow="-4px 0 16px rgba(0, 0, 0, 0.06)",
                        display=rx.breakpoints(initial="flex", md="none"),
                        flex_direction="column",
                    ),
                ),
                display="flex",
                flex_direction="row",
                align_items="stretch",
                width="100%",
                max_width="1336px",
                height=rx.breakpoints(
                    initial="calc(100vh - 20px)",
                    md="calc(100vh - 36px)",
                ),
                background="white",
                border_radius=rx.breakpoints(initial="24px", md="34px"),
                overflow="hidden",
                position="relative",
                box_shadow="0 1px 3px rgba(0, 0, 0, 0.06)",
            ),
            margin_left=rx.breakpoints(initial="0px", lg="200px"),
            width=rx.breakpoints(initial="100%", lg="calc(100% - 200px)"),
            max_width="100%",
            min_width="0",
            height="100vh",
            padding=rx.breakpoints(initial="10px", md="18px"),
            align_items="center",
            justify_content="center",
            display="flex",
            overflow="hidden",
        ),
        _source_preview_modal(),
        width="100%",
        max_width="100vw",
        height="100vh",
        background_color="#F0F2F7",
        overflow="hidden",
        overflow_x="hidden",
        on_mount=ChatState.init_session,
    )
