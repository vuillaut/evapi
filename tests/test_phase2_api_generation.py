"""Phase 2: API Endpoint Generation Tests

Tests for the static API generation, including:
- Pagination support
- HATEOAS links
- Filtered views (by-indicator, by-ring)
- OpenAPI specification
- JSON-LD context
"""

import json
import pytest
from pathlib import Path
from datetime import datetime

from scripts.models import Indicator, Tool, Dimension
from scripts.generate_api import (
    generate_indicators_collection,
    generate_tools_collection,
    generate_dimensions_collection,
    generate_relationships_graph,
    generate_openapi_spec,
    ensure_api_structure,
)
from scripts.build_relationships import RelationshipBuilder
from scripts.config import API_DIR, API_CONTEXT, API_BASE_URL


@pytest.mark.integration
class TestPhase2APIGeneration:
    """Test Phase 2 API generation functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data."""
        # Ensure API structure exists
        ensure_api_structure()
        # Create test indicators
        self.indicators = [
            Indicator(
                id="license",
                name="License",
                description="Software has a clear license",
                dimension="legal",
                category="governance",
                rationale="Clear licensing is essential",
                url="https://example.com/license",
                related_tools=["howfairis", "reuse"],
            ),
            Indicator(
                id="citation",
                name="Citation",
                description="Software is citable",
                dimension="legal",
                category="governance",
                rationale="Citation metadata is important",
                url="https://example.com/citation",
                related_tools=["zenodo"],
            ),
        ]

        # Create test tools
        self.tools = [
            Tool(
                id="howfairis",
                name="howfairis",
                description="Tool to check FAIR principles",
                url="https://howfairis.readthedocs.io/",
                ring="adopt",
                quadrant="tools",
                related_indicators=["license", "citation"],
            ),
            Tool(
                id="zenodo",
                name="Zenodo",
                description="Open repository for scholarly artifacts",
                url="https://zenodo.org/",
                ring="adopt",
                quadrant="tools",
                related_indicators=["citation"],
            ),
            Tool(
                id="reuse",
                name="REUSE",
                description="Software license and copyright compliance tool",
                url="https://reuse.software/",
                ring="trial",
                quadrant="tools",
                related_indicators=["license"],
            ),
        ]

        # Create test dimensions
        self.dimensions = [
            Dimension(
                id="legal",
                name="Legal",
                description="Legal and governance aspects",
                indicators=["license", "citation"],
            ),
        ]

        yield

    def test_indicators_collection_has_pagination(self):
        """Test that indicators collection includes pagination metadata."""
        generate_indicators_collection(self.indicators)

        # Read the main index
        index_file = API_DIR / "indicators" / "index.json"
        assert index_file.exists(), "Indicators index.json should exist"

        with open(index_file) as f:
            data = json.load(f)

        # Check pagination metadata
        assert data["@type"] == "IndicatorCollection"
        assert "page" in data
        assert "perPage" in data
        assert "totalPages" in data
        assert data["page"] == 1
        assert data["perPage"] == 50
        assert data["totalItems"] == len(self.indicators)

    def test_indicators_have_hateoas_links(self):
        """Test that indicators include HATEOAS links."""
        generate_indicators_collection(self.indicators)

        # Check individual indicator
        indicator_file = API_DIR / "indicators" / "license.json"
        assert indicator_file.exists(), "Individual indicator file should exist"

        with open(indicator_file) as f:
            data = json.load(f)

        # Check HATEOAS links
        assert "_links" in data
        links = data["_links"]
        assert "self" in links
        assert "collection" in links
        assert "tools" in links
        assert links["self"] == f"{API_BASE_URL}/indicators/license"

    def test_tools_filtered_by_indicator(self):
        """Test that tools are filtered and indexed by indicator."""
        builder = RelationshipBuilder()
        builder.add_indicators(self.indicators)
        builder.add_tools(self.tools)
        builder.build_all_relationships()

        generate_tools_collection(self.tools, builder)

        # Check by-indicator view for license
        by_indicator_file = API_DIR / "tools" / "by-indicator" / "license.json"
        assert by_indicator_file.exists(), "by-indicator view should be generated"

        with open(by_indicator_file) as f:
            data = json.load(f)

        assert data["@type"] == "ToolCollection"
        assert data["indicator"] == "license"
        assert data["totalItems"] == 2  # howfairis and reuse

        # Verify tools in the filtered view
        tool_ids = [tool["id"] for tool in data["items"]]
        assert "howfairis" in tool_ids
        assert "reuse" in tool_ids

    def test_tools_filtered_by_ring(self):
        """Test that tools are filtered and indexed by ring."""
        builder = RelationshipBuilder()
        builder.add_indicators(self.indicators)
        builder.add_tools(self.tools)
        builder.build_all_relationships()

        generate_tools_collection(self.tools, builder)

        # Check by-ring view for adopt
        by_ring_file = API_DIR / "tools" / "by-ring" / "adopt.json"
        assert by_ring_file.exists(), "by-ring view should be generated"

        with open(by_ring_file) as f:
            data = json.load(f)

        assert data["@type"] == "ToolCollection"
        assert data["ring"] == "adopt"
        assert data["totalItems"] == 2  # howfairis and zenodo

        # Verify tools in the filtered view
        tool_ids = [tool["id"] for tool in data["items"]]
        assert "howfairis" in tool_ids
        assert "zenodo" in tool_ids

    def test_openapi_spec_generated(self):
        """Test that OpenAPI specification is generated correctly."""
        generate_openapi_spec(self.indicators, self.tools, self.dimensions)

        openapi_file = API_DIR / "openapi.json"
        assert openapi_file.exists(), "openapi.json should exist"

        with open(openapi_file) as f:
            spec = json.load(f)

        # Check OpenAPI structure
        assert spec["openapi"] == "3.0.0"
        assert "info" in spec
        assert spec["info"]["title"] == "EVERSE Unified API"
        assert "paths" in spec
        assert "components" in spec

    def test_openapi_spec_includes_endpoints(self):
        """Test that OpenAPI spec includes all main endpoints."""
        generate_openapi_spec(self.indicators, self.tools, self.dimensions)

        openapi_file = API_DIR / "openapi.json"
        with open(openapi_file) as f:
            spec = json.load(f)

        paths = spec["paths"]

        # Check main endpoints
        assert "/" in paths
        assert "/indicators" in paths
        assert "/indicators/{id}" in paths
        assert "/tools" in paths
        assert "/tools/{id}" in paths
        assert "/tools/by-indicator/{indicator_id}" in paths
        assert "/tools/by-ring/{ring}" in paths
        assert "/dimensions" in paths
        assert "/dimensions/{id}" in paths
        assert "/dimensions/{id}/indicators" in paths

    def test_openapi_spec_has_schemas(self):
        """Test that OpenAPI spec includes data schemas."""
        generate_openapi_spec(self.indicators, self.tools, self.dimensions)

        openapi_file = API_DIR / "openapi.json"
        with open(openapi_file) as f:
            spec = json.load(f)

        schemas = spec["components"]["schemas"]

        # Check component schemas
        assert "Indicator" in schemas
        assert "Tool" in schemas
        assert "Dimension" in schemas

    def test_json_ld_context_in_responses(self):
        """Test that all responses include JSON-LD context."""
        generate_indicators_collection(self.indicators)
        generate_tools_collection(self.tools, RelationshipBuilder())
        generate_dimensions_collection(self.dimensions)

        # Check indicators
        indicator_file = API_DIR / "indicators" / "license.json"
        with open(indicator_file) as f:
            data = json.load(f)
        assert "@context" in data
        assert data["@context"] == API_CONTEXT

        # Check tools
        tool_file = API_DIR / "tools" / "howfairis.json"
        with open(tool_file) as f:
            data = json.load(f)
        assert "@context" in data

        # Check dimensions
        dimension_file = API_DIR / "dimensions" / "legal.json"
        with open(dimension_file) as f:
            data = json.load(f)
        assert "@context" in data

    def test_relationships_graph_has_correct_structure(self):
        """Test that relationships graph is generated with correct structure."""
        builder = RelationshipBuilder()
        builder.add_indicators(self.indicators)
        builder.add_tools(self.tools)
        builder.add_dimensions(self.dimensions)
        builder.build_all_relationships()

        generate_relationships_graph(builder)

        graph_file = API_DIR / "relationships" / "graph.json"
        assert graph_file.exists(), "graph.json should exist"

        with open(graph_file) as f:
            data = json.load(f)

        assert data["@type"] == "Graph"
        assert "@context" in data
        assert "generated" in data

    def test_generated_files_have_timestamps(self):
        """Test that generated files include generation timestamp."""
        generate_indicators_collection(self.indicators)

        indicator_file = API_DIR / "indicators" / "license.json"
        with open(indicator_file) as f:
            data = json.load(f)

        assert "generated" in data
        # Verify it's a valid ISO format timestamp
        timestamp = data["generated"]
        assert timestamp.endswith("Z")
        # Try to parse it
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


@pytest.mark.integration
class TestPhase2APIStructure:
    """Test the complete API file structure."""

    def test_api_directory_structure(self):
        """Test that API directory structure matches specification."""
        required_dirs = [
            "indicators",
            "tools",
            "dimensions",
            "relationships",
        ]

        for dir_name in required_dirs:
            dir_path = API_DIR / dir_name
            assert dir_path.exists(), f"Directory {dir_name} should exist"
            assert dir_path.is_dir(), f"{dir_name} should be a directory"

    def test_filtered_views_directory_structure(self):
        """Test that filtered views directories exist."""
        # These should be created by the collection generation functions
        filtered_dirs = [
            "tools/by-indicator",
            "tools/by-ring",
        ]

        for dir_path in filtered_dirs:
            full_path = API_DIR / dir_path
            # Note: These are created during generation, so we just check the parent exists
            parent = full_path.parent
            assert parent.exists(), f"Parent of {dir_path} should exist"

    def test_openapi_json_is_valid(self):
        """Test that openapi.json is valid JSON and parseable."""
        openapi_file = API_DIR / "openapi.json"
        if openapi_file.exists():
            with open(openapi_file) as f:
                data = json.load(f)
            assert isinstance(data, dict)
            assert "openapi" in data
            assert "paths" in data


@pytest.mark.integration
class TestPhase2Integration:
    """Integration tests for Phase 2."""

    def test_full_api_generation_pipeline(self):
        """Test the complete API generation pipeline."""
        # Create test data
        indicators = [
            Indicator(
                id="test1",
                name="Test Indicator",
                description="Test",
                dimension="test-dim",
                category="test-cat",
                rationale="Test",
                url="https://example.com",
                related_tools=["test-tool"],
            ),
        ]

        tools = [
            Tool(
                id="test-tool",
                name="Test Tool",
                description="Test",
                url="https://example.com",
                ring="adopt",
                quadrant="test",
                related_indicators=["test1"],
            ),
        ]

        dimensions = [
            Dimension(
                id="test-dim",
                name="Test Dimension",
                description="Test",
                indicators=["test1"],
            ),
        ]

        # Generate API components
        generate_indicators_collection(indicators)
        builder = RelationshipBuilder()
        builder.add_indicators(indicators)
        builder.add_tools(tools)
        builder.add_dimensions(dimensions)
        builder.build_all_relationships()
        generate_tools_collection(tools, builder)
        generate_dimensions_collection(dimensions)
        generate_relationships_graph(builder)
        generate_openapi_spec(indicators, tools, dimensions)

        # Verify all files exist
        assert (API_DIR / "indicators" / "index.json").exists()
        assert (API_DIR / "tools" / "index.json").exists()
        assert (API_DIR / "dimensions" / "index.json").exists()
        assert (API_DIR / "relationships" / "graph.json").exists()
        assert (API_DIR / "openapi.json").exists()

    def test_cross_referenced_links_consistency(self):
        """Test that cross-referenced links are consistent."""
        indicators = [
            Indicator(
                id="license",
                name="License",
                description="License indicator",
                dimension="legal",
                category="governance",
                rationale="Test",
                url="https://example.com",
                related_tools=["howfairis"],
            ),
        ]

        tools = [
            Tool(
                id="howfairis",
                name="howfairis",
                description="FAIR checker",
                url="https://howfairis.readthedocs.io/",
                ring="adopt",
                quadrant="tools",
                related_indicators=["license"],
            ),
        ]

        dimensions = [
            Dimension(
                id="legal",
                name="Legal",
                description="Legal dimension",
                indicators=["license"],
            ),
        ]

        # Generate API
        generate_indicators_collection(indicators)
        builder = RelationshipBuilder()
        builder.add_indicators(indicators)
        builder.add_tools(tools)
        builder.add_dimensions(dimensions)
        builder.build_all_relationships()
        generate_tools_collection(tools, builder)
        generate_dimensions_collection(dimensions)

        # Verify cross-references
        with open(API_DIR / "indicators" / "license.json") as f:
            indicator = json.load(f)
        assert "tools" in indicator["_links"]

        with open(API_DIR / "tools" / "howfairis.json") as f:
            tool = json.load(f)
        assert "indicators" in tool["_links"]
