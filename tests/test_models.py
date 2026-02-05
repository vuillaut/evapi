"""Tests for data models."""

import pytest
from scripts.models import Indicator, Tool, Dimension


class TestIndicator:
    """Tests for Indicator model."""

    def test_indicator_creation(self):
        """Test creating an indicator."""
        indicator = Indicator(
            id="test",
            name="Test Indicator",
            description="A test indicator",
        )
        assert indicator.id == "test"
        assert indicator.name == "Test Indicator"

    def test_indicator_required_fields(self):
        """Test indicator required fields."""
        with pytest.raises(Exception):
            Indicator(name="Missing ID")


class TestTool:
    """Tests for Tool model."""

    def test_tool_creation(self):
        """Test creating a tool."""
        tool = Tool(
            id="test-tool",
            name="Test Tool",
            ring="adopt",
        )
        assert tool.id == "test-tool"
        assert tool.name == "Test Tool"
        assert tool.ring == "adopt"

    def test_tool_with_indicators(self):
        """Test tool with related indicators."""
        tool = Tool(
            id="test-tool",
            name="Test Tool",
            related_indicators=["indicator1", "indicator2"],
        )
        assert len(tool.related_indicators) == 2


class TestDimension:
    """Tests for Dimension model."""

    def test_dimension_creation(self):
        """Test creating a dimension."""
        dimension = Dimension(
            id="test-dim",
            name="Test Dimension",
            indicators=["ind1", "ind2"],
        )
        assert dimension.id == "test-dim"
        assert len(dimension.indicators) == 2
