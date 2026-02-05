"""Data models for EVERSE Unified API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Indicator(BaseModel):
    """Model for a quality indicator."""

    id: str = Field(..., description="Unique indicator identifier")
    name: str = Field(..., description="Human-readable indicator name")
    description: Optional[str] = Field(None, description="Detailed description")
    dimension: Optional[str] = Field(None, description="Associated dimension ID")
    category: Optional[str] = Field(None, description="Indicator category")
    rationale: Optional[str] = Field(None, description="Why this indicator matters")
    url: Optional[HttpUrl] = Field(None, description="URL to indicator documentation")
    related_tools: List[str] = Field(default_factory=list, description="Related tool IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = {"extra": "allow"}  # Allow additional fields from JSON-LD


class Tool(BaseModel):
    """Model for a quality assessment tool."""

    id: str = Field(..., description="Unique tool identifier")
    name: str = Field(..., description="Tool name")
    description: Optional[str] = Field(None, description="Tool description")
    url: Optional[HttpUrl] = Field(None, description="Tool URL")
    ring: Optional[str] = Field(None, description="TechRadar ring (adopt, trial, assess, hold)")
    quadrant: Optional[str] = Field(None, description="TechRadar quadrant")
    related_indicators: List[str] = Field(default_factory=list, description="Related indicator IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        extra = "allow"  # Allow additional fields


class Dimension(BaseModel):
    """Model for a quality dimension."""

    id: str = Field(..., description="Unique dimension identifier")
    name: str = Field(..., description="Dimension name")
    description: Optional[str] = Field(None, description="Description")
    indicators: List[str] = Field(default_factory=list, description="Associated indicator IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        extra = "allow"


class Task(BaseModel):
    """Model for an RSQKit task."""

    id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    role: Optional[str] = Field(None, description="Target role")
    phase: Optional[str] = Field(None, description="Lifecycle phase")
    related_indicators: List[str] = Field(default_factory=list, description="Related indicator IDs")
    related_tools: List[str] = Field(default_factory=list, description="Related tool IDs")
    url: Optional[HttpUrl] = Field(None, description="Task URL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        extra = "allow"


class Pipeline(BaseModel):
    """Model for a quality assessment pipeline."""

    name: str = Field(..., description="Pipeline name")
    description: Optional[str] = Field(None, description="Pipeline description")
    indicators: List[str] = Field(..., description="Indicator IDs in pipeline")
    tools: List[str] = Field(default_factory=list, description="Tool IDs in pipeline")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class RelationshipEdge(BaseModel):
    """Model for a relationship between entities."""

    source_id: str = Field(..., description="Source entity ID")
    source_type: str = Field(..., description="Source entity type")
    target_id: str = Field(..., description="Target entity ID")
    target_type: str = Field(..., description="Target entity type")
    relationship_type: str = Field(..., description="Type of relationship")


class APIResponse(BaseModel):
    """Standard API response wrapper."""

    context: str = Field(..., description="JSON-LD context")
    type: str = Field(..., description="Response type")
    data: Any = Field(..., description="Response data")
    timestamp: str = Field(..., description="Response timestamp")
    version: str = Field("1.0", description="API version")
