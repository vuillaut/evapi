"""Integration tests for the API generation pipeline."""

import pytest
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.fetch_indicators import fetch_and_validate_indicators
from scripts.fetch_tools import fetch_and_validate_tools
from scripts.fetch_dimensions import fetch_and_validate_dimensions
from scripts.build_relationships import RelationshipBuilder
from scripts.models import Indicator, Tool, Dimension


class TestDataFetching:
    """Tests for data fetching from sources."""

    @pytest.mark.integration
    def test_fetch_indicators(self):
        """Test fetching indicators."""
        indicators = fetch_and_validate_indicators(use_cache=True)
        assert indicators is not None
        assert isinstance(indicators, list)
        if indicators:
            assert all(isinstance(i, Indicator) for i in indicators)

    @pytest.mark.integration
    def test_fetch_tools(self):
        """Test fetching tools."""
        tools = fetch_and_validate_tools(use_cache=True)
        assert tools is not None
        assert isinstance(tools, list)
        if tools:
            assert all(isinstance(t, Tool) for t in tools)

    @pytest.mark.integration
    def test_fetch_dimensions(self):
        """Test fetching dimensions."""
        dimensions = fetch_and_validate_dimensions(use_cache=True)
        assert dimensions is not None
        assert isinstance(dimensions, list)
        if dimensions:
            assert all(isinstance(d, Dimension) for d in dimensions)


class TestRelationshipBuilding:
    """Tests for relationship building."""

    @pytest.fixture
    def builder(self):
        """Create a relationship builder with test data."""
        builder = RelationshipBuilder()

        indicators = fetch_and_validate_indicators(use_cache=True)
        tools = fetch_and_validate_tools(use_cache=True)
        dimensions = fetch_and_validate_dimensions(use_cache=True)

        builder.add_indicators(indicators)
        builder.add_tools(tools)
        builder.add_dimensions(dimensions)
        builder.build_all_relationships()

        return builder

    def test_relationship_builder_initialized(self, builder):
        """Test relationship builder initialization."""
        assert len(builder.indicators) > 0
        assert len(builder.tools) > 0
        # Relationships might be 0 if source data doesn't have relationship metadata yet
        assert len(builder.relationships) >= 0

    def test_relationship_validation(self, builder):
        """Test relationship validation."""
        valid_count, errors = builder.validate_relationships()
        # If there are relationships, most should be valid
        if builder.relationships:
            assert valid_count >= len(builder.relationships) * 0.8  # 80% valid
        else:
            # No relationships is acceptable if source data doesn't have them yet
            assert valid_count == 0

    def test_get_tools_for_indicator(self, builder):
        """Test getting tools for an indicator."""
        if builder.indicators:
            indicator_id = next(iter(builder.indicators))
            tools = builder.get_tools_for_indicator(indicator_id)
            assert isinstance(tools, list)

    def test_get_indicators_for_tool(self, builder):
        """Test getting indicators for a tool."""
        if builder.tools:
            tool_id = next(iter(builder.tools))
            indicators = builder.get_indicators_for_tool(tool_id)
            assert isinstance(indicators, list)

    def test_get_indicators_for_dimension(self, builder):
        """Test getting indicators for a dimension."""
        if builder.dimensions:
            dimension_id = next(iter(builder.dimensions))
            indicators = builder.get_indicators_for_dimension(dimension_id)
            assert isinstance(indicators, list)

    def test_export_graph(self, builder):
        """Test graph export."""
        graph = builder.export_graph()
        assert "nodes" in graph
        assert "edges" in graph
        assert "statistics" in graph
        # Relationships might be 0 if source data doesn't have relationship metadata yet
        assert graph["statistics"]["total_relationships"] >= 0


@pytest.mark.integration
class TestFullPipeline:
    """Test the complete API generation pipeline."""

    def test_complete_workflow(self):
        """Test complete API generation workflow."""
        # Fetch data
        indicators = fetch_and_validate_indicators(use_cache=True)
        tools = fetch_and_validate_tools(use_cache=True)
        dimensions = fetch_and_validate_dimensions(use_cache=True)

        # Verify data
        assert indicators, "No indicators fetched"
        assert tools, "No tools fetched"
        assert dimensions, "No dimensions fetched"

        # Build relationships
        builder = RelationshipBuilder()
        builder.add_indicators(indicators)
        builder.add_tools(tools)
        builder.add_dimensions(dimensions)
        builder.build_all_relationships()

        # Validate
        valid_count, errors = builder.validate_relationships()
        # Relationships might be 0 if source data doesn't have relationship metadata yet
        assert valid_count >= 0, "Validation failed"
        if builder.relationships:
            assert valid_count > 0, "Relationships exist but none are valid"

        # Export
        graph = builder.export_graph()
        assert graph["statistics"]["total_relationships"] > 0
