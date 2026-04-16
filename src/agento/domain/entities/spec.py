"""Spec entity."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Spec(BaseModel):
    """Specification entity."""

    id: str = Field(description="Unique spec identifier")
    name: str = Field(description="Spec name")
    description: str = Field(description="Spec description")
    content: str = Field(description="Spec content (markdown)")
    requirements: list[str] = Field(
        default_factory=list,
        description="List of requirements",
    )
    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description="List of acceptance criteria",
    )
    status: str = Field(
        default="draft",
        description="Spec status",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )
