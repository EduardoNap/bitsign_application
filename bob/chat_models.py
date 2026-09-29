"""Database models for chat conversation history."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import reflex as rx
import sqlmodel


class Conversation(rx.Model, table=True):
    """A single conversation session."""

    __tablename__ = "conversations"

    title: str = ""
    session_id: str = sqlmodel.Field(index=True)
    created_at: datetime = sqlmodel.Field(default_factory=datetime.utcnow)
    updated_at: datetime = sqlmodel.Field(default_factory=datetime.utcnow)


class ChatMessageRecord(rx.Model, table=True):
    """A persisted chat message belonging to a conversation."""

    __tablename__ = "chat_messages"

    conversation_id: int = sqlmodel.Field(foreign_key="conversations.id", index=True)
    text: str = ""
    is_user: bool = True
    created_at: datetime = sqlmodel.Field(default_factory=datetime.utcnow)