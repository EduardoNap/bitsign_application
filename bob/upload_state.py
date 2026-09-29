"""Upload state — S3 upload integration for contract PDFs."""

from __future__ import annotations

import os
from datetime import date, datetime

import reflex as rx
import boto3
from botocore.exceptions import ClientError
from sqlalchemy import text


S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_RAW_PREFIX = os.getenv("S3_RAW_PREFIX", "raw/")
REGION = os.getenv("AWS_REGION", "us-east-2")


class UploadResult(rx.Base):
    """A single file upload result."""

    name: str
    status: str  # "success" | "error"
    message: str


class ContractField(rx.Base):
    """A key field/value pair for a contract from RDS."""

    label: str
    value: str


class UploadState(rx.State):
    """Manages PDF uploads to S3 raw/ folder."""

    # UI state
    is_uploading: bool = False
    upload_progress: int = 0
    results: list[UploadResult] = []
    error_message: str = ""
    success_message: str = ""

    # Preview state
    preview_url: str = ""
    preview_filename: str = ""
    preview_panel_mode: str = "empty"  # "empty" | "preview" | "details"

    # Contracts library state
    contract_files: list[str] = []
    contract_search: str = ""
    is_loading_contracts: bool = False

    # Contract details from RDS
    selected_contract: str = ""
    is_loading_details: bool = False
    details_error_message: str = ""
    contract_details_fields: list[ContractField] = []

    _IMPORTANT_RDS_FIELDS: list[tuple[str, str]] = [
        ("contract_name", "Contrato"),
        ("estado", "Estado"),
        ("sucursal_vertiche", "Sucursal"),
        ("renta_mensual", "Renta mensual"),
        ("deposito_garantia", "Depósito garantía"),
        ("fecha_inicio", "Fecha inicio"),
        ("fecha_vencimiento", "Fecha vencimiento"),
        ("arrendador", "Arrendador"),
        ("arrendatario", "Arrendatario"),
        ("ciudad", "Ciudad"),
        ("direccion", "Dirección"),
        ("metodo_pago", "Método de pago"),
        ("dia_pago", "Día de pago"),
        ("duracion_meses", "Duración (meses)"),
    ]

    @staticmethod
    def _format_field_value(column_name: str, value: object) -> str:
        """Format DB values for UI display."""
        if value is None:
            return "-"

        if isinstance(value, (date, datetime)):
            return value.strftime("%d/%m/%Y")

        if isinstance(value, (int, float)) and column_name in {"renta_mensual", "deposito_garantia"}:
            return f"${float(value):,.2f}"

        return str(value)

    def _clear_messages(self) -> None:
        self.error_message = ""
        self.success_message = ""

    def set_contract_search(self, value: str) -> None:
        """Update search text for contract listing."""
        self.contract_search = value

    def open_contract_from_list(self, filename: str) -> None:
        """Open preview from the contracts listing."""
        self.selected_contract = filename
        self._generate_preview(filename)
        self.preview_panel_mode = "preview" if self.preview_url else "empty"

    def open_contract_details_from_rds(self, filename: str) -> None:
        """Load important contract fields from RDS and show details panel."""
        self.selected_contract = filename
        self.is_loading_details = True
        self.details_error_message = ""
        self.contract_details_fields = []
        self.preview_panel_mode = "details"

        contract_base = filename.rsplit(".", 1)[0]

        try:
            with rx.session() as session:
                # Discover real columns in contracts to avoid runtime errors.
                cols_rows = session.execute(
                    text(
                        """
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name = 'contracts'
                          AND table_schema = ANY (current_schemas(false))
                        """
                    )
                ).fetchall()

                available_columns = {r.column_name for r in cols_rows}
                selected_fields = [
                    (col, label)
                    for col, label in self._IMPORTANT_RDS_FIELDS
                    if col in available_columns
                ]

                if "contract_name" not in available_columns:
                    self.details_error_message = (
                        "No se encontró la columna contract_name en la tabla contracts."
                    )
                    return

                if not selected_fields:
                    self.details_error_message = (
                        "No hay campos compatibles para mostrar en la tabla contracts."
                    )
                    return

                select_sql = ", ".join(col for col, _ in selected_fields)
                row = session.execute(
                    text(
                        f"""
                        SELECT {select_sql}
                        FROM contracts
                        WHERE lower(contract_name) = lower(:contract_base)
                           OR lower(contract_name) = lower(:filename)
                           OR lower(contract_name) LIKE lower(:contract_like)
                        ORDER BY
                            CASE
                                WHEN lower(contract_name) = lower(:contract_base) THEN 0
                                WHEN lower(contract_name) = lower(:filename) THEN 1
                                ELSE 2
                            END
                        LIMIT 1
                        """
                    ),
                    {
                        "contract_base": contract_base,
                        "filename": filename,
                        "contract_like": f"{contract_base}%",
                    },
                ).fetchone()

                if not row:
                    self.details_error_message = (
                        "No se encontró ese contrato en la base de datos RDS."
                    )
                    return

                mapped = row._mapping
                self.contract_details_fields = [
                    ContractField(
                        label=label,
                        value=self._format_field_value(col, mapped.get(col)),
                    )
                    for col, label in selected_fields
                ]

        except Exception as exc:
            self.details_error_message = (
                f"No se pudieron cargar los campos desde RDS: {str(exc)[:140]}"
            )
        finally:
            self.is_loading_details = False

    @rx.var
    def filtered_contract_files(self) -> list[str]:
        """Contracts list filtered by search query."""
        query = self.contract_search.strip().lower()
        if not query:
            return self.contract_files
        return [name for name in self.contract_files if query in name.lower()]

    def load_contracts(self) -> None:
        """Load all uploaded contract filenames from S3 raw/ prefix."""
        self.is_loading_contracts = True
        try:
            s3 = boto3.client("s3", region_name=REGION)
            paginator = s3.get_paginator("list_objects_v2")
            files: list[str] = []

            for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=S3_RAW_PREFIX):
                for item in page.get("Contents", []):
                    key = item.get("Key", "")
                    if not key or key.endswith("/") or key == S3_RAW_PREFIX:
                        continue
                    filename = key[len(S3_RAW_PREFIX):] if key.startswith(S3_RAW_PREFIX) else key
                    if filename and filename.lower().endswith(".pdf"):
                        files.append(filename)

            self.contract_files = sorted(set(files), key=str.lower)
        except ClientError as exc:
            error = exc.response.get("Error", {})
            code = error.get("Code", "Unknown")
            self.error_message = f"No se pudo cargar el listado de contratos (S3: {code})."
        except Exception:
            self.error_message = "No se pudo cargar el listado de contratos."
        finally:
            self.is_loading_contracts = False

    def clear_results(self) -> None:
        """Reset everything so the user can upload again."""
        self.results = []
        self.upload_progress = 0
        self.preview_url = ""
        self.preview_filename = ""
        self.preview_panel_mode = "empty"
        self.selected_contract = ""
        self.is_loading_details = False
        self.details_error_message = ""
        self.contract_details_fields = []
        self._clear_messages()

    def close_preview(self) -> None:
        """Close the PDF preview."""
        self.preview_url = ""
        self.preview_filename = ""
        self.preview_panel_mode = "empty"

    def _generate_preview(self, filename: str) -> None:
        """Generate a presigned URL for previewing the uploaded PDF."""
        try:
            s3 = boto3.client("s3", region_name=REGION)
            s3_key = f"{S3_RAW_PREFIX}{filename}"
            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": S3_BUCKET, "Key": s3_key},
                ExpiresIn=3600,
            )
            self.preview_url = url
            self.preview_filename = filename
        except Exception:
            self.preview_url = ""
            self.preview_filename = ""

    async def handle_upload(self, files: list[rx.UploadFile]) -> None:
        """Upload PDF files to the configured S3 bucket/prefix.

        Uses yield (NOT background=True) so rx.upload_files passes files correctly.
        """
        self._clear_messages()

        if not files:
            self.error_message = "No se seleccionaron archivos."
            yield
            return

        self.is_uploading = True
        self.upload_progress = 0
        self.results = []
        yield  # show loading state immediately

        s3 = boto3.client("s3", region_name=REGION)
        total = len(files)
        batch_results: list[UploadResult] = []

        for idx, file in enumerate(files, start=1):
            name = file.filename or "unknown.pdf"

            # Validate PDF extension
            if not name.lower().endswith(".pdf"):
                batch_results.append(
                    UploadResult(name=name, status="error", message="No es un archivo PDF")
                )
                self.upload_progress = int((idx / total) * 100)
                yield
                continue

            try:
                file_bytes = await file.read()

                if len(file_bytes) == 0:
                    batch_results.append(
                        UploadResult(name=name, status="error", message="Archivo vacío")
                    )
                    self.upload_progress = int((idx / total) * 100)
                    yield
                    continue

                s3_key = f"{S3_RAW_PREFIX}{name}"
                s3.put_object(
                    Bucket=S3_BUCKET,
                    Key=s3_key,
                    Body=file_bytes,
                    ContentType="application/pdf",
                )
                batch_results.append(
                    UploadResult(name=name, status="success", message="Subido correctamente")
                )

            except ClientError as exc:
                error = exc.response.get("Error", {})
                code = error.get("Code", "Unknown")
                detail = error.get("Message", "")

                if code == "AccessDenied":
                    detail = (
                        f"Sin permiso PutObject en s3://{S3_BUCKET}/{S3_RAW_PREFIX}*"
                    )
                elif code in {"InvalidAccessKeyId", "SignatureDoesNotMatch"}:
                    detail = "Credenciales AWS inválidas"

                batch_results.append(
                    UploadResult(
                        name=name,
                        status="error",
                        message=(
                            f"Error S3: {code}"
                            if not detail
                            else f"Error S3: {code} ({detail[:100]})"
                        ),
                    )
                )
            except Exception as exc:
                batch_results.append(
                    UploadResult(
                        name=name, status="error", message=f"Error: {str(exc)[:80]}"
                    )
                )

            self.upload_progress = int((idx / total) * 100)
            yield  # update progress between files

        # Finalize
        ok = sum(1 for r in batch_results if r.status == "success")
        fail = len(batch_results) - ok

        self.results = batch_results
        self.is_uploading = False

        if ok and not fail:
            self.success_message = (
                f"{'Archivo subido' if ok == 1 else f'{ok} archivos subidos'} "
                "correctamente."
            )
            self.load_contracts()
            # Generate preview for the last successfully uploaded file
            last_ok = next(
                (r.name for r in reversed(batch_results) if r.status == "success"),
                None,
            )
            if last_ok:
                self._generate_preview(last_ok)
        elif ok and fail:
            self.success_message = f"{ok} subido(s), {fail} con error."
            self.load_contracts()
        elif fail:
            if any("AccessDenied" in r.message for r in batch_results):
                self.error_message = (
                    "No se pudo subir ningún archivo. AWS rechazó el acceso al bucket (AccessDenied)."
                )
            else:
                self.error_message = "No se pudo subir ningún archivo."

        yield  # final UI update
