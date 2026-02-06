"""Main script to generate the EVERSE Unified API."""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
from urllib.parse import urlencode
from collections import defaultdict

import click

# Add parent directory to path to allow imports from anywhere
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.fetch_indicators import fetch_and_validate_indicators
from scripts.fetch_tools import fetch_and_validate_tools
from scripts.fetch_dimensions import fetch_and_validate_dimensions
from scripts.build_relationships import RelationshipBuilder
from scripts.validate import validate_collections, validate_api_files
from scripts.models import APIResponse, Indicator, Tool, Dimension
from scripts.config import API_DIR, API_VERSION, API_CONTEXT, API_BASE_URL

logger = logging.getLogger(__name__)


def ensure_api_structure() -> None:
    """Ensure API directory structure exists."""
    subdirs = [
        "indicators",
        "tools",
        "dimensions",
        "relationships",
        "tasks",
        "pipelines",
    ]

    for subdir in subdirs:
        (API_DIR / subdir).mkdir(parents=True, exist_ok=True)

    logger.info("API directory structure ensured")


def generate_api_root() -> None:
    """Generate the API root endpoint."""
    logger.info("Generating API root...")

    data = {
        "@context": API_CONTEXT,
        "@type": "APIRoot",
        "version": API_VERSION,
        "title": "EVERSE Unified API",
        "description": "Unified API for EVERSE research software quality services",
        "endpoints": {
            "indicators": f"{API_BASE_URL}/indicators/",
            "tools": f"{API_BASE_URL}/tools/",
            "dimensions": f"{API_BASE_URL}/dimensions/",
            "relationships": f"{API_BASE_URL}/relationships/",
            "tasks": f"{API_BASE_URL}/tasks/",
            "pipelines": f"{API_BASE_URL}/pipelines/",
        },
        "generated": datetime.utcnow().isoformat() + "Z",
    }

    output_file = API_DIR / "index.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Generated API root: {output_file}")


def generate_indicators_collection(indicators: List[Indicator]) -> None:
    """Generate indicators collection endpoint with pagination."""
    logger.info("Generating indicators collection...")

    # Generate pagination (50 items per page)
    items_per_page = 50
    total_items = len(indicators)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    for page in range(1, total_pages + 1):
        start_idx = (page - 1) * items_per_page
        end_idx = min(page * items_per_page, total_items)
        page_items = indicators[start_idx:end_idx]

        items_data = []
        for indicator in page_items:
            item = indicator.model_dump(mode="json")
            item["_links"] = {
                "self": f"{API_BASE_URL}/indicators/{indicator.id}",
                "tools": f"{API_BASE_URL}/tools?indicator={indicator.id}",
            }
            items_data.append(item)

        # Build links
        links = {
            "self": f"{API_BASE_URL}/indicators?page={page}",
        }
        if page > 1:
            links["first"] = f"{API_BASE_URL}/indicators?page=1"
            links["prev"] = f"{API_BASE_URL}/indicators?page={page - 1}"
        if page < total_pages:
            links["next"] = f"{API_BASE_URL}/indicators?page={page + 1}"
            links["last"] = f"{API_BASE_URL}/indicators?page={total_pages}"

        data = {
            "@context": API_CONTEXT,
            "@type": "IndicatorCollection",
            "name": "Indicators",
            "description": "Collection of all quality indicators",
            "totalItems": total_items,
            "page": page,
            "perPage": items_per_page,
            "totalPages": total_pages,
            "items": items_data,
            "_links": links,
            "generated": datetime.utcnow().isoformat() + "Z",
        }

        output_file = API_DIR / "indicators" / f"index_p{page}.json" if page > 1 else API_DIR / "indicators" / "index.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Generated indicators collection ({total_pages} pages)")

    # Generate individual indicator files
    for indicator in indicators:
        # Create safe filename from URL ID (extract last part after slash)
        safe_filename = indicator.id.split("/")[-1] if "/" in indicator.id else indicator.id

        indicator_data = {
            "@context": API_CONTEXT,
            "@type": "Indicator",
            **indicator.model_dump(mode="json"),
            "_links": {
                "self": f"{API_BASE_URL}/indicators/{safe_filename}",
                "collection": f"{API_BASE_URL}/indicators",
                "tools": f"{API_BASE_URL}/tools?indicator={indicator.id}",
                "in-dimensions": f"{API_BASE_URL}/dimensions?indicator={indicator.id}",
            },
            "generated": datetime.utcnow().isoformat() + "Z",
        }

        output_file = API_DIR / "indicators" / f"{safe_filename}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(indicator_data, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Generated {len(indicators)} individual indicator files")


def generate_tools_collection(tools: List[Tool], builder: RelationshipBuilder) -> None:
    """Generate tools collection endpoint with pagination and filtered views."""
    logger.info("Generating tools collection...")

    # Generate pagination (50 items per page)
    items_per_page = 50
    total_items = len(tools)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    for page in range(1, total_pages + 1):
        start_idx = (page - 1) * items_per_page
        end_idx = min(page * items_per_page, total_items)
        page_items = tools[start_idx:end_idx]

        items_data = []
        for tool in page_items:
            item = tool.model_dump(mode="json")
            item["_links"] = {
                "self": f"{API_BASE_URL}/tools/{tool.id}",
                "indicators": f"{API_BASE_URL}/indicators?tool={tool.id}",
            }
            items_data.append(item)

        # Build links
        links = {
            "self": f"{API_BASE_URL}/tools?page={page}",
            "by-ring": f"{API_BASE_URL}/tools/by-ring",
        }
        if page > 1:
            links["first"] = f"{API_BASE_URL}/tools?page=1"
            links["prev"] = f"{API_BASE_URL}/tools?page={page - 1}"
        if page < total_pages:
            links["next"] = f"{API_BASE_URL}/tools?page={page + 1}"
            links["last"] = f"{API_BASE_URL}/tools?page={total_pages}"

        data = {
            "@context": API_CONTEXT,
            "@type": "ToolCollection",
            "name": "Tools",
            "description": "Collection of all quality assessment tools",
            "totalItems": total_items,
            "page": page,
            "perPage": items_per_page,
            "totalPages": total_pages,
            "items": items_data,
            "_links": links,
            "generated": datetime.utcnow().isoformat() + "Z",
        }

        output_file = API_DIR / "tools" / f"index_p{page}.json" if page > 1 else API_DIR / "tools" / "index.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Generated tools collection ({total_pages} pages)")

    # Generate individual tool files
    for tool in tools:
        # Create safe filename from URL ID (extract last part after slash)
        safe_filename = tool.id.split("/")[-1] if "/" in tool.id else tool.id

        tool_data = {
            "@context": API_CONTEXT,
            "@type": "Tool",
            **tool.model_dump(mode="json"),
            "_links": {
                "self": f"{API_BASE_URL}/tools/{safe_filename}",
                "collection": f"{API_BASE_URL}/tools",
                "indicators": f"{API_BASE_URL}/indicators?tool={tool.id}",
            },
            "generated": datetime.utcnow().isoformat() + "Z",
        }

        output_file = API_DIR / "tools" / f"{safe_filename}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(tool_data, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Generated {len(tools)} individual tool files")

    # Generate by-indicator filtered views
    logger.info("Generating tools by-indicator views...")
    (API_DIR / "tools" / "by-indicator").mkdir(parents=True, exist_ok=True)

    indicators_to_tools = defaultdict(list)
    for tool in tools:
        if hasattr(tool, "related_indicators") and tool.related_indicators:
            for indicator_id in tool.related_indicators:
                indicators_to_tools[indicator_id].append(tool)

    for indicator_id, tools_list in indicators_to_tools.items():
        items_data = []
        for tool in tools_list:
            item = tool.model_dump(mode="json")
            item["_links"] = {
                "self": f"{API_BASE_URL}/tools/{tool.id}",
            }
            items_data.append(item)

        data = {
            "@context": API_CONTEXT,
            "@type": "ToolCollection",
            "indicator": indicator_id,
            "description": f"Tools that measure indicator {indicator_id}",
            "totalItems": len(tools_list),
            "items": items_data,
            "_links": {
                "self": f"{API_BASE_URL}/tools/by-indicator/{indicator_id}",
                "collection": f"{API_BASE_URL}/tools",
                "indicator": f"{API_BASE_URL}/indicators/{indicator_id}",
            },
            "generated": datetime.utcnow().isoformat() + "Z",
        }

        output_file = API_DIR / "tools" / "by-indicator" / f"{indicator_id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Generated {len(indicators_to_tools)} by-indicator views")

    # Generate by-ring filtered views
    logger.info("Generating tools by-ring views...")
    (API_DIR / "tools" / "by-ring").mkdir(parents=True, exist_ok=True)

    tools_by_ring = defaultdict(list)
    for tool in tools:
        if hasattr(tool, "ring") and tool.ring:
            tools_by_ring[tool.ring].append(tool)

    for ring, tools_list in sorted(tools_by_ring.items()):
        items_data = []
        for tool in tools_list:
            item = tool.model_dump(mode="json")
            item["_links"] = {
                "self": f"{API_BASE_URL}/tools/{tool.id}",
            }
            items_data.append(item)

        data = {
            "@context": API_CONTEXT,
            "@type": "ToolCollection",
            "ring": ring,
            "description": f"Tools in {ring} ring",
            "totalItems": len(tools_list),
            "items": items_data,
            "_links": {
                "self": f"{API_BASE_URL}/tools/by-ring/{ring}",
                "collection": f"{API_BASE_URL}/tools",
            },
            "generated": datetime.utcnow().isoformat() + "Z",
        }

        output_file = API_DIR / "tools" / "by-ring" / f"{ring}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Generated {len(tools_by_ring)} by-ring views")


def generate_dimensions_collection(dimensions: List[Dimension]) -> None:
    """Generate dimensions collection endpoint with pagination."""
    logger.info("Generating dimensions collection...")

    # Generate pagination (50 items per page)
    items_per_page = 50
    total_items = len(dimensions)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    for page in range(1, total_pages + 1):
        start_idx = (page - 1) * items_per_page
        end_idx = min(page * items_per_page, total_items)
        page_items = dimensions[start_idx:end_idx]

        items_data = []
        for dimension in page_items:
            item = dimension.model_dump(mode="json")
            item["_links"] = {
                "self": f"{API_BASE_URL}/dimensions/{dimension.id}",
                "indicators": f"{API_BASE_URL}/dimensions/{dimension.id}/indicators",
            }
            items_data.append(item)

        # Build links
        links = {
            "self": f"{API_BASE_URL}/dimensions?page={page}",
        }
        if page > 1:
            links["first"] = f"{API_BASE_URL}/dimensions?page=1"
            links["prev"] = f"{API_BASE_URL}/dimensions?page={page - 1}"
        if page < total_pages:
            links["next"] = f"{API_BASE_URL}/dimensions?page={page + 1}"
            links["last"] = f"{API_BASE_URL}/dimensions?page={total_pages}"

        data = {
            "@context": API_CONTEXT,
            "@type": "DimensionCollection",
            "name": "Dimensions",
            "description": "Collection of all quality dimensions",
            "totalItems": total_items,
            "page": page,
            "perPage": items_per_page,
            "totalPages": total_pages,
            "items": items_data,
            "_links": links,
            "generated": datetime.utcnow().isoformat() + "Z",
        }

        output_file = API_DIR / "dimensions" / f"index_p{page}.json" if page > 1 else API_DIR / "dimensions" / "index.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Generated dimensions collection ({total_pages} pages)")

    # Generate individual dimension files
    for dimension in dimensions:
        # Create safe filename from URL ID (extract last part after slash)
        safe_filename = dimension.id.split("/")[-1] if "/" in dimension.id else dimension.id

        dimension_data = {
            "@context": API_CONTEXT,
            "@type": "Dimension",
            **dimension.model_dump(mode="json"),
            "_links": {
                "self": f"{API_BASE_URL}/dimensions/{safe_filename}",
                "collection": f"{API_BASE_URL}/dimensions",
                "indicators": f"{API_BASE_URL}/dimensions/{dimension.id}/indicators",
            },
            "generated": datetime.utcnow().isoformat() + "Z",
        }

        output_file = API_DIR / "dimensions" / f"{safe_filename}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(dimension_data, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Generated {len(dimensions)} individual dimension files")


def generate_relationships_graph(builder: RelationshipBuilder) -> None:
    """Generate relationships graph."""
    logger.info("Generating relationships graph...")

    graph_data = {
        "@context": API_CONTEXT,
        "@type": "Graph",
        "name": "Entity Relationships",
        "description": "Knowledge graph of relationships between indicators, tools, and dimensions",
        **builder.export_graph(),
        "generated": datetime.utcnow().isoformat() + "Z",
    }

    output_file = API_DIR / "relationships" / "graph.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Generated relationships graph: {output_file}")


def generate_openapi_spec(
    indicators: List[Indicator],
    tools: List[Tool],
    dimensions: List[Dimension],
) -> None:
    """Generate OpenAPI 3.0 specification."""
    logger.info("Generating OpenAPI specification...")

    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "EVERSE Unified API",
            "description": "Unified API for EVERSE research software quality services",
            "version": API_VERSION,
            "contact": {
                "name": "EVERSE Team",
            },
            "license": {
                "name": "Apache 2.0",
            },
        },
        "servers": [
            {
                "url": API_BASE_URL,
                "description": "EVERSE Unified API",
            }
        ],
        "paths": {
            "/": {
                "get": {
                    "operationId": "getApiRoot",
                    "summary": "API Root",
                    "description": "Get the API root with links to all endpoints",
                    "tags": ["Root"],
                    "responses": {
                        "200": {
                            "description": "API root information",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "@context": {"type": "string"},
                                            "@type": {"type": "string"},
                                            "version": {"type": "string"},
                                            "endpoints": {"type": "object"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/indicators": {
                "get": {
                    "operationId": "listIndicators",
                    "summary": "List Indicators",
                    "description": "Get paginated list of all quality indicators",
                    "tags": ["Indicators"],
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Page number (default: 1)",
                            "schema": {"type": "integer", "default": 1},
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "description": "Items per page (default: 50, max: 100)",
                            "schema": {"type": "integer", "default": 50},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Indicators collection",
                        }
                    },
                }
            },
            "/indicators/{id}": {
                "get": {
                    "operationId": "getIndicator",
                    "summary": "Get Indicator",
                    "description": "Get a specific indicator by ID",
                    "tags": ["Indicators"],
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "description": "Indicator ID",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Indicator details",
                        },
                        "404": {
                            "description": "Indicator not found",
                        },
                    },
                }
            },
            "/tools": {
                "get": {
                    "operationId": "listTools",
                    "summary": "List Tools",
                    "description": "Get paginated list of all quality assessment tools",
                    "tags": ["Tools"],
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Page number (default: 1)",
                            "schema": {"type": "integer", "default": 1},
                        },
                        {
                            "name": "indicator",
                            "in": "query",
                            "description": "Filter by indicator ID",
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "ring",
                            "in": "query",
                            "description": "Filter by ring (adopt, trial, assess, hold)",
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Tools collection",
                        }
                    },
                }
            },
            "/tools/{id}": {
                "get": {
                    "operationId": "getTool",
                    "summary": "Get Tool",
                    "description": "Get a specific tool by ID",
                    "tags": ["Tools"],
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "description": "Tool ID",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Tool details",
                        },
                        "404": {
                            "description": "Tool not found",
                        },
                    },
                }
            },
            "/tools/by-indicator/{indicator_id}": {
                "get": {
                    "operationId": "getToolsByIndicator",
                    "summary": "Get Tools by Indicator",
                    "description": "Get all tools that measure a specific indicator",
                    "tags": ["Tools"],
                    "parameters": [
                        {
                            "name": "indicator_id",
                            "in": "path",
                            "required": True,
                            "description": "Indicator ID",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Tools for indicator",
                        },
                        "404": {
                            "description": "Indicator not found",
                        },
                    },
                }
            },
            "/tools/by-ring/{ring}": {
                "get": {
                    "operationId": "getToolsByRing",
                    "summary": "Get Tools by Ring",
                    "description": "Get all tools in a specific ring",
                    "tags": ["Tools"],
                    "parameters": [
                        {
                            "name": "ring",
                            "in": "path",
                            "required": True,
                            "description": "Ring value (adopt, trial, assess, hold)",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Tools by ring",
                        },
                        "404": {
                            "description": "Ring not found",
                        },
                    },
                }
            },
            "/dimensions": {
                "get": {
                    "operationId": "listDimensions",
                    "summary": "List Dimensions",
                    "description": "Get paginated list of all quality dimensions",
                    "tags": ["Dimensions"],
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Page number (default: 1)",
                            "schema": {"type": "integer", "default": 1},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Dimensions collection",
                        }
                    },
                }
            },
            "/dimensions/{id}": {
                "get": {
                    "operationId": "getDimension",
                    "summary": "Get Dimension",
                    "description": "Get a specific dimension by ID",
                    "tags": ["Dimensions"],
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "description": "Dimension ID",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Dimension details",
                        },
                        "404": {
                            "description": "Dimension not found",
                        },
                    },
                }
            },
            "/dimensions/{id}/indicators": {
                "get": {
                    "operationId": "getDimensionIndicators",
                    "summary": "Get Dimension Indicators",
                    "description": "Get all indicators for a specific dimension",
                    "tags": ["Dimensions"],
                    "parameters": [
                        {
                            "name": "id",
                            "in": "path",
                            "required": True,
                            "description": "Dimension ID",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Indicators for dimension",
                        },
                        "404": {
                            "description": "Dimension not found",
                        },
                    },
                }
            },
            "/relationships/graph": {
                "get": {
                    "operationId": "getRelationshipsGraph",
                    "summary": "Get Relationships Graph",
                    "description": "Get the complete knowledge graph of relationships",
                    "tags": ["Relationships"],
                    "responses": {
                        "200": {
                            "description": "Relationships graph",
                        }
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "Indicator": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "dimension": {"type": "string"},
                        "category": {"type": "string"},
                        "rationale": {"type": "string"},
                        "url": {"type": "string"},
                        "_links": {"type": "object"},
                    },
                    "required": ["id", "name", "description"],
                },
                "Tool": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "url": {"type": "string"},
                        "ring": {"type": "string"},
                        "quadrant": {"type": "string"},
                        "_links": {"type": "object"},
                    },
                    "required": ["id", "name", "description"],
                },
                "Dimension": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "indicators": {"type": "array", "items": {"type": "string"}},
                        "_links": {"type": "object"},
                    },
                    "required": ["id", "name", "description"],
                },
            }
        },
        "tags": [
            {
                "name": "Root",
                "description": "API root endpoint",
            },
            {
                "name": "Indicators",
                "description": "Quality indicators",
            },
            {
                "name": "Tools",
                "description": "Quality assessment tools",
            },
            {
                "name": "Dimensions",
                "description": "Quality dimensions",
            },
            {
                "name": "Relationships",
                "description": "Entity relationships graph",
            },
        ],
    }

    output_file = API_DIR / "openapi.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

    logger.info(f"✓ Generated OpenAPI specification: {output_file}")


@click.command()
@click.option("--skip-cache", is_flag=True, help="Skip using cached data")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def main(skip_cache: bool, verbose: bool) -> None:
    """Generate the EVERSE Unified API."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger.info("=" * 60)
    logger.info("EVERSE Unified API Generator - Phase 2")
    logger.info("=" * 60)

    try:
        # Fetch and validate data
        logger.info("\n1. Fetching data from sources...")
        indicators = fetch_and_validate_indicators(use_cache=not skip_cache)
        tools = fetch_and_validate_tools(use_cache=not skip_cache)
        dimensions = fetch_and_validate_dimensions(use_cache=not skip_cache)

        if not (indicators and tools and dimensions):
            logger.error("Failed to fetch required data")
            return

        # Validate data
        logger.info("\n2. Validating data...")
        is_valid, errors = validate_collections(indicators, tools, dimensions)
        if not is_valid:
            logger.error("Data validation failed")
            for error in errors:
                logger.error(f"  - {error}")
            return

        # Build relationships
        logger.info("\n3. Building relationships...")
        builder = RelationshipBuilder()
        builder.add_indicators(indicators)
        builder.add_tools(tools)
        builder.add_dimensions(dimensions)
        builder.build_all_relationships()

        # Validate relationships
        valid_count, errors = builder.validate_relationships()
        if errors:
            for error in errors:
                logger.error(f"  - {error}")

        # Save relationships to cache
        builder.save_to_cache()

        # Generate API
        logger.info("\n4. Generating API endpoints with pagination and filtered views...")
        ensure_api_structure()
        generate_api_root()
        generate_indicators_collection(indicators)
        generate_tools_collection(tools, builder)
        generate_dimensions_collection(dimensions)
        generate_relationships_graph(builder)

        # Generate OpenAPI specification
        logger.info("\n5. Generating OpenAPI specification...")
        generate_openapi_spec(indicators, tools, dimensions)

        # Generate health check endpoints
        logger.info("\n6. Generating health check endpoints...")
        from scripts.health_check import generate_health_endpoint, generate_status_endpoint, generate_dashboard, generate_landing_page

        generate_health_endpoint()
        generate_status_endpoint()
        generate_dashboard()
        generate_landing_page()

        # Validate generated API
        logger.info("\n7. Validating generated API...")
        api_valid, api_errors = validate_api_files(API_DIR)
        if not api_valid:
            logger.error("API validation failed")
            for error in api_errors:
                logger.error(f"  - {error}")
            return

        logger.info("\n" + "=" * 60)
        logger.info("✓ API generation completed successfully!")
        logger.info("=" * 60)
        logger.info(f"API location: {API_DIR}")
        logger.info(f"Indicators: {len(indicators)}")
        logger.info(f"Tools: {len(tools)}")
        logger.info(f"Dimensions: {len(dimensions)}")
        logger.info(f"Relationships: {valid_count}")
        logger.info(f"OpenAPI spec: {API_DIR / 'openapi.json'}")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
