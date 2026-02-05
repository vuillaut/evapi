"""API endpoint generator - creates static JSON files for the API."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from models import Indicator, Tool, Dimension
from config import API_DIR, API_VERSION, API_CONTEXT, API_BASE_URL

logger = logging.getLogger(__name__)


class APIGenerator:
    """Generate static API endpoints as JSON files."""

    def __init__(self, api_dir: Path = API_DIR):
        """Initialize the generator."""
        self.api_dir = api_dir
        self.api_version = API_VERSION
        self.api_context = API_CONTEXT
        self.base_url = API_BASE_URL

    def _save_json(self, data: Dict[str, Any], filepath: Path) -> None:
        """Save data as JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _add_hateoas_links(self, data: Dict[str, Any], entity_id: str = None, entity_type: str = None) -> Dict[str, Any]:
        """Add HATEOAS links to response."""
        if "links" not in data:
            data["links"] = {}

        # Self link
        if entity_type and entity_id:
            data["links"]["self"] = f"{self.base_url}/{entity_type}/{entity_id}"
        elif entity_type:
            data["links"]["self"] = f"{self.base_url}/{entity_type}/"

        # Root link
        data["links"]["root"] = f"{self.base_url}/"

        return data

    def _add_timestamps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add timestamp information."""
        if "timestamp" not in data:
            data["generated"] = datetime.utcnow().isoformat() + "Z"
        return data

    def generate_root_endpoint(self) -> None:
        """Generate the API root endpoint."""
        logger.info("Generating API root endpoint...")

        data = {
            "@context": self.api_context,
            "@type": "APIRoot",
            "version": self.api_version,
            "title": "EVERSE Unified API",
            "description": "Unified API for EVERSE research software quality services",
            "documentation": "https://github.com/EVERSE-ResearchSoftware/unified-api/tree/main/docs",
            "endpoints": {
                "indicators": {"url": f"{self.base_url}/indicators/", "description": "Quality indicators"},
                "tools": {"url": f"{self.base_url}/tools/", "description": "Assessment tools"},
                "dimensions": {"url": f"{self.base_url}/dimensions/", "description": "Quality dimensions"},
                "relationships": {"url": f"{self.base_url}/relationships/", "description": "Entity relationships"},
                "openapi": {"url": f"{self.base_url}/openapi.json", "description": "OpenAPI specification"},
            },
        }
        data = self._add_timestamps(data)

        output_file = self.api_dir / "index.json"
        self._save_json(data, output_file)
        logger.info(f"✓ Generated root endpoint: {output_file}")

    def generate_indicators(self, indicators: List[Indicator]) -> None:
        """Generate indicators collection and individual endpoints."""
        logger.info(f"Generating {len(indicators)} indicator endpoints...")

        # Generate collection
        collection_data = {
            "@context": self.api_context,
            "@type": "Collection",
            "name": "Quality Indicators",
            "description": "Collection of all quality indicators",
            "totalItems": len(indicators),
            "items": [
                {
                    "id": ind.id,
                    "name": ind.name,
                    "description": ind.description,
                    "dimension": ind.dimension,
                    "url": f"{self.base_url}/indicators/{ind.id}",
                }
                for ind in indicators
            ],
        }
        collection_data = self._add_hateoas_links(collection_data, entity_type="indicators")
        collection_data = self._add_timestamps(collection_data)

        output_file = self.api_dir / "indicators" / "index.json"
        self._save_json(collection_data, output_file)
        logger.info(f"✓ Generated indicators collection: {output_file}")

        # Generate individual indicator files
        for indicator in indicators:
            indicator_data = {
                "@context": self.api_context,
                "@type": "Indicator",
                "id": indicator.id,
                "name": indicator.name,
                "description": indicator.description,
                "dimension": indicator.dimension,
                "category": indicator.category,
                "rationale": indicator.rationale,
                "url": indicator.url,
                "related_tools": indicator.related_tools,
            }
            # Remove None values
            indicator_data = {k: v for k, v in indicator_data.items() if v is not None}
            indicator_data = self._add_hateoas_links(indicator_data, indicator.id, "indicators")
            indicator_data = self._add_timestamps(indicator_data)

            output_file = self.api_dir / "indicators" / f"{indicator.id}.json"
            self._save_json(indicator_data, output_file)

        logger.info(f"✓ Generated {len(indicators)} individual indicator files")

    def generate_indicators_by_dimension(self, indicators: List[Indicator]) -> None:
        """Generate indicators grouped by dimension."""
        logger.info("Generating indicators by dimension...")

        # Group indicators by dimension
        by_dimension: Dict[str, List[Indicator]] = {}
        for indicator in indicators:
            if indicator.dimension:
                if indicator.dimension not in by_dimension:
                    by_dimension[indicator.dimension] = []
                by_dimension[indicator.dimension].append(indicator)

        # Create directory
        by_dim_dir = self.api_dir / "indicators" / "by-dimension"

        for dimension_id, inds in by_dimension.items():
            data = {
                "@context": self.api_context,
                "@type": "Collection",
                "name": f"Indicators in {dimension_id}",
                "dimension": dimension_id,
                "totalItems": len(inds),
                "items": [
                    {
                        "id": ind.id,
                        "name": ind.name,
                        "url": f"{self.base_url}/indicators/{ind.id}",
                    }
                    for ind in inds
                ],
            }
            data = self._add_timestamps(data)

            output_file = by_dim_dir / f"{dimension_id}.json"
            self._save_json(data, output_file)

        logger.info(f"✓ Generated {len(by_dimension)} dimension filtered views")

    def generate_tools(self, tools: List[Tool]) -> None:
        """Generate tools collection and individual endpoints."""
        logger.info(f"Generating {len(tools)} tool endpoints...")

        # Generate collection
        collection_data = {
            "@context": self.api_context,
            "@type": "Collection",
            "name": "Quality Assessment Tools",
            "description": "Collection of all quality assessment tools",
            "totalItems": len(tools),
            "items": [
                {
                    "id": tool.id,
                    "name": tool.name,
                    "description": tool.description,
                    "ring": tool.ring,
                    "url": f"{self.base_url}/tools/{tool.id}",
                }
                for tool in tools
            ],
        }
        collection_data = self._add_hateoas_links(collection_data, entity_type="tools")
        collection_data = self._add_timestamps(collection_data)

        output_file = self.api_dir / "tools" / "index.json"
        self._save_json(collection_data, output_file)
        logger.info(f"✓ Generated tools collection: {output_file}")

        # Generate individual tool files
        for tool in tools:
            tool_data = {
                "@context": self.api_context,
                "@type": "Tool",
                "id": tool.id,
                "name": tool.name,
                "description": tool.description,
                "url": tool.url,
                "ring": tool.ring,
                "quadrant": tool.quadrant,
                "related_indicators": tool.related_indicators,
            }
            # Remove None values
            tool_data = {k: v for k, v in tool_data.items() if v is not None}
            tool_data = self._add_hateoas_links(tool_data, tool.id, "tools")
            tool_data = self._add_timestamps(tool_data)

            output_file = self.api_dir / "tools" / f"{tool.id}.json"
            self._save_json(tool_data, output_file)

        logger.info(f"✓ Generated {len(tools)} individual tool files")

    def generate_tools_by_ring(self, tools: List[Tool]) -> None:
        """Generate tools grouped by ring."""
        logger.info("Generating tools by ring...")

        # Group tools by ring
        by_ring: Dict[str, List[Tool]] = {}
        for tool in tools:
            if tool.ring:
                if tool.ring not in by_ring:
                    by_ring[tool.ring] = []
                by_ring[tool.ring].append(tool)

        # Create directory
        by_ring_dir = self.api_dir / "tools" / "by-ring"

        for ring_id, tool_list in by_ring.items():
            data = {
                "@context": self.api_context,
                "@type": "Collection",
                "name": f"Tools in {ring_id} Ring",
                "ring": ring_id,
                "totalItems": len(tool_list),
                "items": [
                    {
                        "id": tool.id,
                        "name": tool.name,
                        "url": f"{self.base_url}/tools/{tool.id}",
                    }
                    for tool in tool_list
                ],
            }
            data = self._add_timestamps(data)

            output_file = by_ring_dir / f"{ring_id}.json"
            self._save_json(data, output_file)

        logger.info(f"✓ Generated {len(by_ring)} ring filtered views")

    def generate_tools_by_indicator(self, tools: List[Tool]) -> None:
        """Generate tools grouped by indicator."""
        logger.info("Generating tools by indicator...")

        # Group tools by indicator
        by_indicator: Dict[str, List[Tool]] = {}
        for tool in tools:
            for indicator_id in tool.related_indicators:
                if indicator_id not in by_indicator:
                    by_indicator[indicator_id] = []
                by_indicator[indicator_id].append(tool)

        # Create directory
        by_indicator_dir = self.api_dir / "tools" / "by-indicator"

        for indicator_id, tool_list in by_indicator.items():
            data = {
                "@context": self.api_context,
                "@type": "Collection",
                "name": f"Tools for {indicator_id} Indicator",
                "indicator": indicator_id,
                "totalItems": len(tool_list),
                "items": [
                    {
                        "id": tool.id,
                        "name": tool.name,
                        "ring": tool.ring,
                        "url": f"{self.base_url}/tools/{tool.id}",
                    }
                    for tool in tool_list
                ],
            }
            data = self._add_timestamps(data)

            output_file = by_indicator_dir / f"{indicator_id}.json"
            self._save_json(data, output_file)

        logger.info(f"✓ Generated {len(by_indicator)} indicator filtered views")

    def generate_dimensions(self, dimensions: List[Dimension]) -> None:
        """Generate dimensions collection and individual endpoints."""
        logger.info(f"Generating {len(dimensions)} dimension endpoints...")

        # Generate collection
        collection_data = {
            "@context": self.api_context,
            "@type": "Collection",
            "name": "Quality Dimensions",
            "description": "Collection of all quality dimensions",
            "totalItems": len(dimensions),
            "items": [
                {
                    "id": dim.id,
                    "name": dim.name,
                    "description": dim.description,
                    "indicator_count": len(dim.indicators),
                    "url": f"{self.base_url}/dimensions/{dim.id}",
                }
                for dim in dimensions
            ],
        }
        collection_data = self._add_hateoas_links(collection_data, entity_type="dimensions")
        collection_data = self._add_timestamps(collection_data)

        output_file = self.api_dir / "dimensions" / "index.json"
        self._save_json(collection_data, output_file)
        logger.info(f"✓ Generated dimensions collection: {output_file}")

        # Generate individual dimension files
        for dimension in dimensions:
            dimension_data = {
                "@context": self.api_context,
                "@type": "Dimension",
                "id": dimension.id,
                "name": dimension.name,
                "description": dimension.description,
                "indicators": dimension.indicators,
                "indicator_count": len(dimension.indicators),
            }
            # Remove None values
            dimension_data = {k: v for k, v in dimension_data.items() if v is not None}
            dimension_data = self._add_hateoas_links(dimension_data, dimension.id, "dimensions")
            dimension_data = self._add_timestamps(dimension_data)

            output_file = self.api_dir / "dimensions" / f"{dimension.id}.json"
            self._save_json(dimension_data, output_file)

        logger.info(f"✓ Generated {len(dimensions)} individual dimension files")

    def generate_relationships_graph(self, graph_data: Dict[str, Any]) -> None:
        """Generate relationship graph endpoint."""
        logger.info("Generating relationship graph...")

        data = {
            "@context": self.api_context,
            "@type": "Graph",
            "name": "Entity Relationship Graph",
            "description": "Knowledge graph of relationships between indicators, tools, and dimensions",
            **graph_data,
        }
        data = self._add_timestamps(data)

        output_file = self.api_dir / "relationships" / "graph.json"
        self._save_json(data, output_file)
        logger.info(f"✓ Generated relationship graph: {output_file}")

    def generate_openapi_spec(self, indicators: List[Indicator], tools: List[Tool], dimensions: List[Dimension]) -> None:
        """Generate OpenAPI specification."""
        logger.info("Generating OpenAPI specification...")

        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "EVERSE Unified API",
                "description": "Unified API for EVERSE research software quality services",
                "version": self.api_version,
                "contact": {
                    "name": "EVERSE Technical Team",
                    "url": "https://everse.software/",
                },
                "license": {
                    "name": "Apache 2.0",
                    "url": "https://www.apache.org/licenses/LICENSE-2.0",
                },
            },
            "servers": [
                {
                    "url": self.base_url,
                    "description": "Production API",
                }
            ],
            "paths": {
                "/": {
                    "get": {
                        "summary": "API Root",
                        "description": "Get available endpoints",
                        "responses": {
                            "200": {
                                "description": "API root information",
                            }
                        },
                    }
                },
                "/indicators/": {
                    "get": {
                        "summary": "List Indicators",
                        "description": "Get all quality indicators",
                        "parameters": [
                            {
                                "name": "dimension",
                                "in": "query",
                                "description": "Filter by dimension",
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "List of indicators",
                            }
                        },
                    }
                },
                "/indicators/{id}": {
                    "get": {
                        "summary": "Get Indicator",
                        "description": "Get specific indicator details",
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
                "/tools/": {
                    "get": {
                        "summary": "List Tools",
                        "description": "Get all quality assessment tools",
                        "parameters": [
                            {
                                "name": "ring",
                                "in": "query",
                                "description": "Filter by ring (adopt, trial, assess, hold)",
                                "schema": {"type": "string", "enum": ["adopt", "trial", "assess", "hold"]},
                            },
                            {
                                "name": "quadrant",
                                "in": "query",
                                "description": "Filter by quadrant",
                                "schema": {"type": "string"},
                            },
                        ],
                        "responses": {
                            "200": {
                                "description": "List of tools",
                            }
                        },
                    }
                },
                "/tools/{id}": {
                    "get": {
                        "summary": "Get Tool",
                        "description": "Get specific tool details",
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
                        "summary": "Get Tools for Indicator",
                        "description": "Get all tools that measure a specific indicator",
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
                                "description": "List of tools for the indicator",
                            }
                        },
                    }
                },
                "/dimensions/": {
                    "get": {
                        "summary": "List Dimensions",
                        "description": "Get all quality dimensions",
                        "responses": {
                            "200": {
                                "description": "List of dimensions",
                            }
                        },
                    }
                },
                "/dimensions/{id}": {
                    "get": {
                        "summary": "Get Dimension",
                        "description": "Get specific dimension details",
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
                "/relationships/graph": {
                    "get": {
                        "summary": "Get Relationship Graph",
                        "description": "Get knowledge graph of all relationships",
                        "parameters": [
                            {
                                "name": "format",
                                "in": "query",
                                "description": "Output format",
                                "schema": {"type": "string", "enum": ["json", "graphviz"]},
                            },
                            {
                                "name": "depth",
                                "in": "query",
                                "description": "Relationship depth",
                                "schema": {"type": "integer", "default": 2},
                            },
                        ],
                        "responses": {
                            "200": {
                                "description": "Relationship graph",
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
                            "related_tools": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "Tool": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "url": {"type": "string", "format": "uri"},
                            "ring": {"type": "string", "enum": ["adopt", "trial", "assess", "hold"]},
                            "related_indicators": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "Dimension": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "indicators": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                }
            },
        }

        output_file = self.api_dir / "openapi.json"
        self._save_json(spec, output_file)
        logger.info(f"✓ Generated OpenAPI specification: {output_file}")
