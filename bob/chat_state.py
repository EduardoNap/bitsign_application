"""Chat state — Bedrock Agent integration with conversation history."""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Any
from urllib.parse import unquote, urlparse

import reflex as rx
import boto3
from botocore.config import Config
from pydantic import BaseModel
from sqlmodel import select, col

from bob.chat_models import Conversation, ChatMessageRecord


class ChatSource(rx.Base):
    """A single citation/source attached to an assistant message."""

    title: str
    location: str
    snippet: str = ""
    full_text: str = ""


class ChatMessage(rx.Base):
    """A single chat message (in-memory for rendering)."""

    text: str
    is_user: bool
    sources: list[ChatSource] = []


class ConversationSummary(rx.Base):
    """Lightweight conversation info for the history panel."""

    id: int
    title: str
    session_id: str
    date_label: str


class ChatState(rx.State):
    """Manages chat conversation with the Bedrock Agent + history."""

    messages: list[ChatMessage] = []
    current_input: str = ""
    is_loading: bool = False
    session_id: str = ""
    show_landing: bool = True
    show_history: bool = False
    show_source_preview: bool = False
    source_preview_title: str = ""
    source_preview_location: str = ""
    source_preview_text: str = ""

    # Current conversation tracking
    _current_conversation_id: int = 0

    # History list
    conversations: list[ConversationSummary] = []

    # ── Configuration ──────────────────────────────────────
    AGENT_ID: str = os.getenv("BEDROCK_AGENT_ID", "")
    AGENT_ALIAS_ID: str = os.getenv("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")
    REGION: str = os.getenv("AWS_REGION", "us-east-2")
    ENABLE_BEDROCK_TRACE: bool = True
    BEDROCK_READ_TIMEOUT_SECONDS: int = 180
    BEDROCK_CONNECT_TIMEOUT_SECONDS: int = 10

    @staticmethod
    def _truncate(text: str, max_len: int = 240) -> str:
        """Trim long source snippets for compact cards."""
        clean = text.strip()
        if len(clean) <= max_len:
            return clean
        return clean[: max_len - 3] + "..."

    @staticmethod
    def _extract_file_name(raw: str) -> str:
        """Extract just the filename from URI/path-like strings."""
        if not raw:
            return ""
        value = raw.strip()
        parsed = urlparse(value)
        path = parsed.path if parsed.scheme else value
        name = unquote(path.split("?")[0].split("#")[0].rstrip("/").split("/")[-1])
        return name

    @staticmethod
    def _reference_location(
        location: dict[str, Any], metadata: dict[str, Any] | None = None
    ) -> str:
        """Extract a human-readable source location from Bedrock reference."""
        if not location:
            location = {}

        loc_type = str(location.get("type", "")).upper()
        if loc_type == "S3":
            return location.get("s3Location", {}).get("uri", "S3")
        if loc_type == "WEB":
            return location.get("webLocation", {}).get("url", "Web")
        if loc_type == "CONFLUENCE":
            return location.get("confluenceLocation", {}).get("url", "Confluence")
        if loc_type == "SHAREPOINT":
            return location.get("sharePointLocation", {}).get("url", "SharePoint")
        if loc_type == "SALESFORCE":
            return location.get("salesforceLocation", {}).get("url", "Salesforce")
        if loc_type == "KENDRA":
            return location.get("kendraDocumentLocation", {}).get("uri", "Kendra")
        if loc_type == "CUSTOM":
            return location.get("customDocumentLocation", {}).get("id", "Custom")
        if loc_type == "SQL":
            return location.get("sqlLocation", {}).get("query", "SQL")

        # Fallback: in some KB responses the URI is only present in metadata.
        metadata = metadata or {}
        preferred_meta_keys = (
            "x-amz-bedrock-kb-source-uri",
            "source_uri",
            "sourceUrl",
            "url",
            "uri",
        )
        for key in preferred_meta_keys:
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        for value in metadata.values():
            if isinstance(value, str) and value.startswith(("s3://", "http://", "https://")):
                return value

        return "Fuente desconocida"

    @staticmethod
    def _reference_full_text(content: dict[str, Any]) -> str:
        """Extract full source text from Bedrock reference content."""
        if not content:
            return ""

        text = str(content.get("text") or "").strip()
        if text:
            return text

        row = content.get("row") or []
        if isinstance(row, list) and row:
            parts: list[str] = []
            for cell in row[:3]:
                if isinstance(cell, dict):
                    col = cell.get("columnName")
                    val = cell.get("columnValue")
                    if col and val is not None:
                        parts.append(f"{col}: {val}")
            if parts:
                return " | ".join(parts)

        return ""

    @staticmethod
    def _reference_snippet(content: dict[str, Any]) -> str:
        """Extract a compact preview snippet for source cards."""
        full = ChatState._reference_full_text(content)
        if not full:
            return ""
        return ChatState._truncate(full, max_len=260)

    @staticmethod
    def _reference_title(metadata: dict[str, Any], location: str) -> str:
        """Resolve a display title for source cards."""
        # Prefer a real filename (from location or metadata URI fields).
        candidate_values: list[str] = [location]
        if metadata:
            for key in (
                "x-amz-bedrock-kb-source-uri",
                "source_uri",
                "sourceUrl",
                "url",
                "uri",
                "source",
                "filename",
                "file_name",
                "name",
                "title",
                "document_title",
            ):
                val = metadata.get(key)
                if isinstance(val, str) and val.strip():
                    candidate_values.append(val.strip())

            # Fallback: use the first non-empty metadata string.
            for val in metadata.values():
                if isinstance(val, str) and val.strip():
                    candidate_values.append(val.strip())

        for value in candidate_values:
            file_name = ChatState._extract_file_name(value)
            if file_name:
                return file_name

        return "Documento"

    def _extract_sources_from_references(
        self, references: list[dict[str, Any]]
    ) -> list[ChatSource]:
        """Build source cards from a list of Bedrock retrieved references."""
        parsed: list[ChatSource] = []
        for ref in references:
            metadata = ref.get("metadata") or {}
            location = self._reference_location(ref.get("location") or {}, metadata)
            full_text = self._reference_full_text(ref.get("content") or {})
            snippet = ChatState._truncate(full_text, max_len=260) if full_text else ""
            title = self._reference_title(metadata, location)

            if location == "Fuente desconocida" and not full_text and title == "Documento":
                continue

            parsed.append(
                ChatSource(
                    title=title,
                    location=location,
                    snippet=snippet,
                    full_text=full_text,
                )
            )
        return parsed

    def open_source_preview(self, title: str, location: str, full_text: str) -> None:
        """Open source preview modal with full chunk text."""
        self.source_preview_title = title
        self.source_preview_location = location
        self.source_preview_text = (
            full_text.strip() if full_text.strip() else "Esta referencia no incluye texto completo."
        )
        self.show_source_preview = True

    def close_source_preview(self) -> None:
        """Close source preview modal."""
        self.show_source_preview = False

    def _extract_sources_from_chunk(self, chunk: dict[str, Any]) -> list[ChatSource]:
        """Collect citation references from one Bedrock completion chunk."""
        attribution = chunk.get("attribution") or {}
        citations = attribution.get("citations") or []
        parsed: list[ChatSource] = []

        for citation in citations:
            references = citation.get("retrievedReferences") or []
            if isinstance(references, list):
                parsed.extend(self._extract_sources_from_references(references))

        return parsed

    def _extract_sources_from_trace(self, trace_event: dict[str, Any]) -> list[ChatSource]:
        """Collect retrievedReferences from trace payloads (knowledge base lookups)."""
        parsed: list[ChatSource] = []

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                refs = node.get("retrievedReferences")
                if isinstance(refs, list):
                    parsed.extend(self._extract_sources_from_references(refs))
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(trace_event)
        return parsed

    def init_session(self) -> None:
        """Create a session ID on first load and load history."""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        self._load_conversations()

    def _load_conversations(self) -> None:
        """Load all conversations from the database."""
        try:
            with rx.session() as session:
                rows = session.exec(
                    select(Conversation)
                    .order_by(col(Conversation.updated_at).desc())
                ).all()

                self.conversations = [
                    ConversationSummary(
                        id=row.id,
                        title=row.title[:60] if row.title else "Conversación",
                        session_id=row.session_id,
                        date_label=row.updated_at.strftime("%d/%m/%Y %H:%M")
                        if row.updated_at
                        else "",
                    )
                    for row in rows
                ]
        except Exception as exc:
            print(f"[ChatState] Error loading conversations: {exc}")
            self.conversations = []

    def _save_message(self, text: str, is_user: bool) -> None:
        """Save a message to the current conversation."""
        try:
            with rx.session() as session:
                # Create conversation on first user message
                if self._current_conversation_id == 0 and is_user:
                    conv = Conversation(
                        title=text[:80],
                        session_id=self.session_id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )
                    session.add(conv)
                    session.commit()
                    session.refresh(conv)
                    self._current_conversation_id = conv.id

                if self._current_conversation_id > 0:
                    msg = ChatMessageRecord(
                        conversation_id=self._current_conversation_id,
                        text=text,
                        is_user=is_user,
                        created_at=datetime.utcnow(),
                    )
                    session.add(msg)

                    # Update conversation timestamp
                    conv = session.get(Conversation, self._current_conversation_id)
                    if conv:
                        conv.updated_at = datetime.utcnow()
                        session.add(conv)

                    session.commit()
        except Exception as exc:
            print(f"[ChatState] Error saving message: {exc}")

    def set_input(self, value: str) -> None:
        self.current_input = value

    def use_suggestion(self, text: str) -> None:
        """Fill the input with a suggestion card's text."""
        self.current_input = text

    def toggle_history(self) -> None:
        """Toggle the history side panel."""
        self.show_history = not self.show_history
        if self.show_history:
            self._load_conversations()

    def clear_chat(self) -> None:
        """Start a new conversation."""
        self.messages = []
        self.session_id = str(uuid.uuid4())
        self._current_conversation_id = 0
        self.show_landing = True
        self.show_history = False

    def load_conversation(self, conv_id: int) -> None:
        """Load a past conversation by ID."""
        try:
            with rx.session() as session:
                conv = session.get(Conversation, conv_id)
                if not conv:
                    return

                msgs = session.exec(
                    select(ChatMessageRecord)
                    .where(ChatMessageRecord.conversation_id == conv_id)
                    .order_by(col(ChatMessageRecord.created_at).asc())
                ).all()

                self.messages = [
                    ChatMessage(text=m.text, is_user=m.is_user, sources=[]) for m in msgs
                ]
                self.session_id = conv.session_id
                self._current_conversation_id = conv.id
                self.show_landing = False
                self.show_history = False

        except Exception as exc:
            print(f"[ChatState] Error loading conversation: {exc}")

    def delete_conversation(self, conv_id: int) -> None:
        """Delete a conversation and its messages."""
        try:
            with rx.session() as session:
                # Delete messages first
                msgs = session.exec(
                    select(ChatMessageRecord).where(
                        ChatMessageRecord.conversation_id == conv_id
                    )
                ).all()
                for m in msgs:
                    session.delete(m)

                # Delete conversation
                conv = session.get(Conversation, conv_id)
                if conv:
                    session.delete(conv)

                session.commit()

            # If we deleted the active conversation, reset
            if self._current_conversation_id == conv_id:
                self.clear_chat()

            self._load_conversations()

        except Exception as exc:
            print(f"[ChatState] Error deleting conversation: {exc}")

    def handle_key_down(self, key: str) -> None:
        """Submit on Enter key."""
        if key == "Enter" and not self.is_loading:
            return ChatState.send_message

    async def send_message(self) -> None:
        """Send the current input to the Bedrock Agent and persist."""
        question = self.current_input.strip()
        if not question or self.is_loading:
            return

        # Add user message
        self.messages.append(ChatMessage(text=question, is_user=True))
        self.current_input = ""
        self.is_loading = True
        self.show_landing = False
        yield  # show user bubble + loading indicator

        # Persist user message
        self._save_message(question, is_user=True)

        # Call Bedrock Agent
        try:
            client = boto3.client(
                "bedrock-agent-runtime",
                region_name=self.REGION,
                config=Config(
                    read_timeout=self.BEDROCK_READ_TIMEOUT_SECONDS,
                    connect_timeout=self.BEDROCK_CONNECT_TIMEOUT_SECONDS,
                    retries={"max_attempts": 2, "mode": "standard"},
                ),
            )
            response = client.invoke_agent(
                agentId=self.AGENT_ID,
                agentAliasId=self.AGENT_ALIAS_ID,
                sessionId=self.session_id,
                inputText=question,
                enableTrace=self.ENABLE_BEDROCK_TRACE,
            )
            answer = ""
            sources: list[ChatSource] = []
            seen_sources: set[str] = set()
            for event in response.get("completion", []):
                chunk = event.get("chunk")
                if chunk:
                    if chunk.get("bytes"):
                        answer += chunk["bytes"].decode("utf-8")

                    for source in self._extract_sources_from_chunk(chunk):
                        source_key = f"{source.location}|{source.full_text[:80]}"
                        if source_key in seen_sources:
                            continue
                        seen_sources.add(source_key)
                        sources.append(source)

                trace_event = event.get("trace")
                if trace_event:
                    for source in self._extract_sources_from_trace(trace_event):
                        source_key = f"{source.location}|{source.full_text[:80]}"
                        if source_key in seen_sources:
                            continue
                        seen_sources.add(source_key)
                        sources.append(source)

            if not answer:
                answer = "No pude encontrar una respuesta. Intenta reformular tu pregunta."
            print(f"[ChatState] Bedrock returned {len(sources)} reference(s).")
        except Exception as e:
            answer = f"Error al consultar el agente: {str(e)}"
            sources = []

        # Add agent response
        self.messages.append(ChatMessage(text=answer, is_user=False, sources=sources))
        self.is_loading = False

        # Persist agent response and refresh history
        self._save_message(answer, is_user=False)
        self._load_conversations()

        yield  # final UI update
