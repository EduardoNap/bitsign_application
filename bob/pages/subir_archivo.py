"""Styled upload page — wired to S3 via UploadState. Two-panel layout."""

from __future__ import annotations

import reflex as rx

from bob.components.sidebar import sidebar
from bob.upload_state import ContractField, UploadState, UploadResult


def _result_row(result: UploadResult) -> rx.Component:
    """Single upload result row with status icon."""
    return rx.hstack(
        rx.icon(
            rx.cond(result.status == "success", "check-circle", "x-circle"),
            size=18,
            color=rx.cond(result.status == "success", "#22C55E", "#EF4444"),
        ),
        rx.text(
            result.name,
            font_weight="600",
            color="#2B3674",
            font_size="14px",
        ),
        rx.text(
            result.message,
            color="#A3AED0",
            font_size="13px",
        ),
        spacing="3",
        align="center",
        width="100%",
    )


def _progress_bar() -> rx.Component:
    """Upload progress bar."""
    return rx.cond(
        UploadState.is_uploading,
        rx.box(
            rx.box(
                width=f"{UploadState.upload_progress}%",
                height="6px",
                background="linear-gradient(180deg, #422AFB 0%, #6A53FA 100%)",
                border_radius="3px",
                transition="width 0.3s ease",
            ),
            width="100%",
            height="6px",
            background_color="#E9EDF7",
            border_radius="3px",
            overflow="hidden",
            margin_top="12px",
        ),
    )


def _selected_files_panel() -> rx.Component:
    """Show currently selected files from the upload control."""
    selected = rx.selected_files("contract_upload")
    return rx.cond(
        selected.length() > 0,
        rx.vstack(
            rx.text(
                "Archivos seleccionados",
                font_size="14px",
                font_weight="700",
                color="#2B3674",
            ),
            rx.foreach(
                selected,
                lambda filename: rx.hstack(
                    rx.icon("file-text", size=14, color="#422AFB"),
                    rx.text(filename, color="#A3AED0", font_size="13px"),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
            ),
            spacing="2",
            width="100%",
            margin_top="12px",
            padding="12px",
            border="1px solid #E9EDF7",
            border_radius="12px",
            background_color="#F8FAFD",
            align="start",
        ),
    )


def _results_panel() -> rx.Component:
    """Results section shown after upload completes."""
    return rx.cond(
        UploadState.results.length() > 0,
        rx.vstack(
            rx.hstack(
                rx.text(
                    "Resultados",
                    font_size="15px",
                    font_weight="700",
                    color="#2B3674",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("x", size=14),
                    on_click=UploadState.clear_results,
                    variant="ghost",
                    size="1",
                    cursor="pointer",
                    color="#A3AED0",
                ),
                width="100%",
                align="center",
            ),
            rx.foreach(UploadState.results, _result_row),
            spacing="3",
            width="100%",
            padding="16px",
            background_color="white",
            border_radius="14px",
            border="1px solid #E9EDF7",
            margin_top="12px",
        ),
    )


def _contract_row(filename: str) -> rx.Component:
    """Single contract row in the contracts library list."""
    return rx.hstack(
        rx.icon("file-text", size=14, color="#422AFB"),
        rx.text(
            filename,
            color="#2B3674",
            font_size="13px",
            no_of_lines=1,
        ),
        rx.spacer(),
        rx.button(
            rx.text("DB", font_size="10px", font_weight="700", color="#422AFB"),
            on_click=UploadState.open_contract_details_from_rds(filename),
            variant="ghost",
            size="1",
            cursor="pointer",
            border="1px solid #DDE3F2",
            border_radius="6px",
            padding="2px 6px",
            min_width="auto",
            _hover={"background": "rgba(66, 42, 251, 0.08)"},
        ),
        rx.button(
            rx.icon("eye", size=14, color="#422AFB"),
            on_click=UploadState.open_contract_from_list(filename),
            variant="ghost",
            size="1",
            cursor="pointer",
            _hover={"background": "rgba(66, 42, 251, 0.08)"},
        ),
        width="100%",
        align="center",
        spacing="2",
        padding="8px 10px",
        border_radius="10px",
        _hover={"background": "rgba(66, 42, 251, 0.05)"},
    )


def _detail_field_row(field: ContractField) -> rx.Component:
    """Single key/value field row in details panel."""
    return rx.hstack(
        rx.text(
            field.label,
            font_size="12px",
            font_weight="700",
            color="#2B3674",
            min_width="130px",
        ),
        rx.text(
            field.value,
            font_size="12px",
            color="#4A5568",
            text_align="right",
            width="100%",
            no_of_lines=2,
        ),
        width="100%",
        align="start",
        spacing="2",
        padding_y="6px",
        border_bottom="1px solid #EDF1F7",
    )


def _contracts_library_panel() -> rx.Component:
    """Searchable list of all uploaded contracts."""
    return rx.vstack(
        rx.hstack(
            rx.text(
                "Contratos subidos",
                font_size="15px",
                font_weight="700",
                color="#2B3674",
            ),
            rx.spacer(),
            rx.cond(
                UploadState.is_loading_contracts,
                rx.spinner(size="1", color="#422AFB"),
                rx.button(
                    rx.icon("refresh-cw", size=14, color="#A3AED0"),
                    on_click=UploadState.load_contracts,
                    variant="ghost",
                    size="1",
                    cursor="pointer",
                    _hover={"background": "rgba(0,0,0,0.04)"},
                ),
            ),
            width="100%",
            align="center",
        ),
        rx.input(
            placeholder="Buscar contrato...",
            value=UploadState.contract_search,
            on_change=UploadState.set_contract_search,
            width="100%",
            height="36px",
            border_radius="10px",
            border="1px solid #E9EDF7",
            background="white",
            color="#2B3674",
            _placeholder={"color": "#A3AED0"},
        ),
        rx.cond(
            UploadState.filtered_contract_files.length() > 0,
            rx.box(
                rx.vstack(
                    rx.foreach(UploadState.filtered_contract_files, _contract_row),
                    spacing="1",
                    width="100%",
                    align="stretch",
                ),
                width="100%",
                flex="1",
                min_height="0",
                height="100%",
                overflow_y="auto",
                border="1px solid #E9EDF7",
                border_radius="12px",
                padding="6px",
                background="#F8FAFD",
            ),
            rx.center(
                rx.text(
                    "No hay contratos que coincidan con la búsqueda.",
                    color="#A3AED0",
                    font_size="13px",
                    text_align="center",
                ),
                width="100%",
                flex="1",
                min_height="0",
                height="100%",
                padding="16px",
                border="1px dashed #E9EDF7",
                border_radius="12px",
                background="#F8FAFD",
            ),
        ),
        spacing="3",
        width="100%",
        flex="1",
        min_height="0",
        margin_top="8px",
        align="stretch",
    )


def _success_alert() -> rx.Component:
    """Green success banner."""
    return rx.cond(
        UploadState.success_message != "",
        rx.hstack(
            rx.icon("check-circle", color="#22C55E", size=18),
            rx.text(
                UploadState.success_message,
                color="#166534",
                font_size="14px",
                font_weight="500",
            ),
            spacing="3",
            align="center",
            padding="12px 16px",
            background_color="#F0FDF4",
            border="1px solid #BBF7D0",
            border_radius="14px",
            width="100%",
            margin_top="12px",
        ),
    )


def _error_alert() -> rx.Component:
    """Red error banner."""
    return rx.cond(
        UploadState.error_message != "",
        rx.hstack(
            rx.icon("alert-circle", color="#EF4444", size=18),
            rx.text(
                UploadState.error_message,
                color="#991B1B",
                font_size="14px",
                font_weight="500",
            ),
            spacing="3",
            align="center",
            padding="12px 16px",
            background_color="#FEF2F2",
            border="1px solid #FECACA",
            border_radius="14px",
            width="100%",
            margin_top="8px",
        ),
    )


def _upload_panel() -> rx.Component:
    """Left card — upload with drag-and-drop."""
    return rx.vstack(
        rx.box(
            # Drag-and-drop zone
            rx.upload(
                rx.vstack(
                    rx.icon("folder", size=44, color="#422AFB", stroke_width=2),
                    rx.text(
                        "Arrastra tus contratos PDF aquí",
                        color="#2B3674",
                        font_size=rx.breakpoints(initial="14px", md="15px"),
                        font_weight="600",
                        text_align="center",
                        line_height="1.35",
                    ),
                    rx.hstack(
                        rx.box(
                            width="60px",
                            height="2px",
                            background_color="#A3AED0",
                        ),
                        rx.text(
                            "O",
                            color="#A3AED0",
                            font_size="14px",
                            font_weight="500",
                        ),
                        rx.box(
                            width="60px",
                            height="2px",
                            background_color="#A3AED0",
                        ),
                        align="center",
                        spacing="4",
                    ),
                    rx.text(
                        "Haz clic para seleccionar archivos",
                        color="#A3AED0",
                        font_size="13px",
                        font_weight="500",
                    ),
                    rx.text(
                        "Solo archivos PDF",
                        color="#A3AED0",
                        font_size="11px",
                        margin_top="-4px",
                    ),
                    spacing="3",
                    align="center",
                    width="100%",
                ),
                id="contract_upload",
                accept={".pdf": ["application/pdf"]},
                multiple=True,
                border="none",
                width="100%",
                height="100%",
                display="flex",
                align_items="center",
                justify_content="center",
                cursor="pointer",
                no_click=False,
                no_drag=False,
            ),
            width="100%",
            flex="none",
            height=rx.breakpoints(initial="180px", md="220px", lg="240px"),
            min_height=rx.breakpoints(initial="180px", md="220px", lg="240px"),
            border="1.5px dashed #E9EDF7",
            border_radius="16px",
            background_color="#F8FAFD",
            padding="14px",
            display="flex",
            align_items="center",
            justify_content="center",
            _hover={"border_color": "#422AFB", "background_color": "#F0F2FF"},
            transition="all 0.2s ease",
        ),
        # Upload button
        rx.button(
            rx.cond(
                UploadState.is_uploading,
                rx.hstack(
                    rx.spinner(size="2", color="white"),
                    rx.text("Subiendo..."),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("cloud-upload", size=18),
                    rx.text("Subir contratos"),
                    spacing="2",
                    align="center",
                ),
            ),
            on_click=UploadState.handle_upload(
                rx.upload_files(upload_id="contract_upload")
            ),
            disabled=UploadState.is_uploading,
            width="100%",
            height="44px",
            border_radius="14px",
            border="none",
            background="linear-gradient(135deg, #6A53FA, #422AFB)",
            color="white",
            font_size="15px",
            font_weight="600",
            cursor="pointer",
            _hover={"opacity": "0.92"},
        ),
        # Progress bar
        _progress_bar(),
        # Selected files feedback
        _selected_files_panel(),
        # Upload results
        _results_panel(),
        # Alerts
        _success_alert(),
        _error_alert(),
        # Contracts library (search + list)
        _contracts_library_panel(),
        spacing="3",
        width="100%",
        height="100%",
        min_height="0",
        padding=rx.breakpoints(initial="12px", md="16px"),
        background="white",
        border_radius=rx.breakpoints(initial="20px", md="24px"),
        box_shadow="0 1px 3px rgba(0, 0, 0, 0.06)",
        align="stretch",
    )


def _preview_panel() -> rx.Component:
    """Right panel — PDF preview card or details from RDS."""
    return rx.box(
        rx.cond(
            UploadState.preview_panel_mode == "details",
            rx.vstack(
                rx.hstack(
                    rx.center(
                        rx.icon("database", size=18, color="#422AFB"),
                        width="36px",
                        height="36px",
                        border_radius="10px",
                        background="rgba(66, 42, 251, 0.08)",
                        flex_shrink="0",
                    ),
                    rx.vstack(
                        rx.text(
                            UploadState.selected_contract,
                            font_size="14px",
                            font_weight="700",
                            color="#2B3674",
                            no_of_lines=1,
                        ),
                        rx.text(
                            "Campos clave desde RDS",
                            font_size="12px",
                            color="#A3AED0",
                        ),
                        spacing="0",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("x", size=14, color="#A3AED0"),
                        on_click=UploadState.close_preview,
                        variant="ghost",
                        size="1",
                        cursor="pointer",
                        _hover={"background": "rgba(0,0,0,0.04)"},
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                    padding="16px 20px",
                    border_bottom="1px solid #E9EDF7",
                ),
                rx.box(
                    rx.cond(
                        UploadState.is_loading_details,
                        rx.center(rx.spinner(size="3", color="#422AFB"), width="100%", height="100%"),
                        rx.cond(
                            UploadState.details_error_message != "",
                            rx.center(
                                rx.text(
                                    UploadState.details_error_message,
                                    color="#991B1B",
                                    font_size="13px",
                                    text_align="center",
                                ),
                                width="100%",
                                height="100%",
                                padding="16px",
                            ),
                            rx.vstack(
                                rx.foreach(UploadState.contract_details_fields, _detail_field_row),
                                spacing="0",
                                width="100%",
                                align="stretch",
                            ),
                        ),
                    ),
                    flex="1",
                    width="100%",
                    overflow_y="auto",
                    padding="10px 16px 16px 16px",
                    border_radius="0 0 20px 20px",
                ),
                spacing="0",
                width="100%",
                height="100%",
                background="white",
                border="1px solid #E9EDF7",
                border_radius="20px",
                overflow="hidden",
                box_shadow="0 2px 8px rgba(0, 0, 0, 0.04)",
            ),
            rx.cond(
                UploadState.preview_url != "",
                rx.vstack(
                    rx.hstack(
                        rx.center(
                            rx.icon("file-text", size=18, color="#422AFB"),
                            width="36px",
                            height="36px",
                            border_radius="10px",
                            background="rgba(66, 42, 251, 0.08)",
                            flex_shrink="0",
                        ),
                        rx.vstack(
                            rx.text(
                                UploadState.preview_filename,
                                font_size="14px",
                                font_weight="700",
                                color="#2B3674",
                                no_of_lines=1,
                            ),
                            rx.text(
                                "Vista previa del contrato",
                                font_size="12px",
                                color="#A3AED0",
                            ),
                            spacing="0",
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("x", size=14, color="#A3AED0"),
                            on_click=UploadState.close_preview,
                            variant="ghost",
                            size="1",
                            cursor="pointer",
                            _hover={"background": "rgba(0,0,0,0.04)"},
                        ),
                        width="100%",
                        align="center",
                        spacing="3",
                        padding="16px 20px",
                        border_bottom="1px solid #E9EDF7",
                    ),
                    rx.box(
                        rx.el.iframe(
                            src=UploadState.preview_url,
                            width="100%",
                            height="100%",
                            border="none",
                        ),
                        flex="1",
                        width="100%",
                        overflow="hidden",
                        border_radius="0 0 20px 20px",
                    ),
                    spacing="0",
                    width="100%",
                    height="100%",
                    background="white",
                    border="1px solid #E9EDF7",
                    border_radius="20px",
                    overflow="hidden",
                    box_shadow="0 2px 8px rgba(0, 0, 0, 0.04)",
                ),
                rx.center(
                    rx.vstack(
                        rx.center(
                            rx.icon("eye", size=32, color="#A3AED0", stroke_width=1.5),
                            width="64px",
                            height="64px",
                            border_radius="16px",
                            background="#F8FAFD",
                            border="1.5px dashed #E9EDF7",
                        ),
                        rx.text(
                            "Vista previa",
                            font_size="18px",
                            font_weight="700",
                            color="#2B3674",
                        ),
                        rx.text(
                            "Selecciona un contrato para ver su contenido aquí",
                            font_size="14px",
                            color="#A3AED0",
                            text_align="center",
                            max_width="240px",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    width="100%",
                    height="100%",
                    background="white",
                    border="1px solid #E9EDF7",
                    border_radius="20px",
                    box_shadow="0 2px 8px rgba(0, 0, 0, 0.04)",
                ),
            ),
        ),
        width="100%",
        height="100%",
    )


def subir_archivo_page() -> rx.Component:
    """Render upload page with split layout when a contract is selected."""
    return rx.box(
        sidebar("subir-archivo"),
        rx.box(
            rx.box(
                rx.box(
                    _upload_panel(),
                    flex="1",
                    min_width="0",
                    height="100%",
                    overflow="hidden",
                ),
                rx.cond(
                    UploadState.preview_panel_mode != "empty",
                    rx.box(
                        _preview_panel(),
                        flex="1",
                        min_width="0",
                        height="100%",
                        overflow="hidden",
                        display=rx.breakpoints(initial="none", md="flex"),
                        flex_direction="column",
                    ),
                    rx.fragment(),
                ),
                display="flex",
                flex_direction=rx.breakpoints(initial="column", md="row"),
                gap=rx.breakpoints(initial="10px", md="18px"),
                width="100%",
                max_width="1336px",
                height=rx.breakpoints(
                    initial="calc(100vh - 20px)",
                    md="calc(100vh - 36px)",
                ),
                overflow="hidden",
            ),
            margin_left=rx.breakpoints(initial="0px", lg="200px"),
            width=rx.breakpoints(initial="100%", lg="calc(100% - 200px)"),
            max_width="100%",
            min_width="0",
            padding=rx.breakpoints(initial="10px", md="18px"),
            align_items="center",
            justify_content="center",
            display="flex",
            min_height="100vh",
        ),
        width="100%",
        max_width="100vw",
        background_color="#F0F2F7",
        min_height="100vh",
        overflow_x="hidden",
        on_mount=UploadState.load_contracts,
    )
