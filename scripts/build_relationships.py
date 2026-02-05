"""Build relationships between EVERSE entities."""

import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple

from scripts.models import Indicator, Tool, Dimension, RelationshipEdge
from scripts.utils import save_json, load_json
from scripts.config import CACHE_DIR

logger = logging.getLogger(__name__)


class RelationshipBuilder:
    """Build and manage relationships between EVERSE entities."""

    def __init__(self):
        """Initialize relationship builder."""
        self.indicators: Dict[str, Indicator] = {}
        self.tools: Dict[str, Tool] = {}
        self.dimensions: Dict[str, Dimension] = {}
        self.relationships: List[RelationshipEdge] = []

    def add_indicators(self, indicators: List[Indicator]) -> None:
        """Add indicators to the builder."""
        for indicator in indicators:
            self.indicators[indicator.id] = indicator
        logger.info(f"Added {len(indicators)} indicators")

    def add_tools(self, tools: List[Tool]) -> None:
        """Add tools to the builder."""
        for tool in tools:
            self.tools[tool.id] = tool
        logger.info(f"Added {len(tools)} tools")

    def add_dimensions(self, dimensions: List[Dimension]) -> None:
        """Add dimensions to the builder."""
        for dimension in dimensions:
            self.dimensions[dimension.id] = dimension
        logger.info(f"Added {len(dimensions)} dimensions")

    def build_tool_to_indicator_relationships(self) -> None:
        """Build relationships from tools to indicators."""
        logger.info("Building tool → indicator relationships...")

        count = 0
        for tool_id, tool in self.tools.items():
            for indicator_id in tool.related_indicators:
                if indicator_id in self.indicators:
                    edge = RelationshipEdge(
                        source_id=tool_id,
                        source_type="Tool",
                        target_id=indicator_id,
                        target_type="Indicator",
                        relationship_type="measures",
                    )
                    self.relationships.append(edge)
                    count += 1
                else:
                    logger.warning(f"Tool {tool_id} references unknown indicator {indicator_id}")

        logger.info(f"Created {count} tool → indicator relationships")

    def build_indicator_to_tool_relationships(self) -> None:
        """Build reverse relationships from indicators to tools."""
        logger.info("Building indicator → tool relationships...")

        count = 0
        for indicator_id, indicator in self.indicators.items():
            for tool_id in indicator.related_tools:
                if tool_id in self.tools:
                    edge = RelationshipEdge(
                        source_id=indicator_id,
                        source_type="Indicator",
                        target_id=tool_id,
                        target_type="Tool",
                        relationship_type="measured_by",
                    )
                    self.relationships.append(edge)
                    count += 1
                else:
                    logger.warning(f"Indicator {indicator_id} references unknown tool {tool_id}")

        logger.info(f"Created {count} indicator → tool relationships")

    def build_dimension_to_indicator_relationships(self) -> None:
        """Build relationships from dimensions to indicators."""
        logger.info("Building dimension → indicator relationships...")

        count = 0
        for dimension_id, dimension in self.dimensions.items():
            for indicator_id in dimension.indicators:
                if indicator_id in self.indicators:
                    edge = RelationshipEdge(
                        source_id=dimension_id,
                        source_type="Dimension",
                        target_id=indicator_id,
                        target_type="Indicator",
                        relationship_type="contains",
                    )
                    self.relationships.append(edge)
                    count += 1
                else:
                    logger.warning(f"Dimension {dimension_id} references unknown indicator {indicator_id}")

        logger.info(f"Created {count} dimension → indicator relationships")

    def build_indicator_to_dimension_relationships(self) -> None:
        """Build reverse relationships from indicators to dimensions."""
        logger.info("Building indicator → dimension relationships...")

        count = 0
        for indicator in self.indicators.values():
            if indicator.dimension:
                if indicator.dimension in self.dimensions:
                    edge = RelationshipEdge(
                        source_id=indicator.id,
                        source_type="Indicator",
                        target_id=indicator.dimension,
                        target_type="Dimension",
                        relationship_type="part_of",
                    )
                    self.relationships.append(edge)
                    count += 1
                else:
                    logger.warning(f"Indicator {indicator.id} references unknown dimension {indicator.dimension}")

        logger.info(f"Created {count} indicator → dimension relationships")

    def build_all_relationships(self) -> None:
        """Build all relationships."""
        logger.info("Building all relationships...")
        self.build_tool_to_indicator_relationships()
        self.build_indicator_to_tool_relationships()
        self.build_dimension_to_indicator_relationships()
        self.build_indicator_to_dimension_relationships()
        logger.info(f"Total relationships built: {len(self.relationships)}")

    def get_tools_for_indicator(self, indicator_id: str) -> List[Tool]:
        """Get all tools that measure a specific indicator."""
        tool_ids = set()
        for rel in self.relationships:
            if rel.target_id == indicator_id and rel.relationship_type == "measures":
                tool_ids.add(rel.source_id)

        return [self.tools[tool_id] for tool_id in tool_ids if tool_id in self.tools]

    def get_indicators_for_tool(self, tool_id: str) -> List[Indicator]:
        """Get all indicators measured by a specific tool."""
        indicator_ids = set()
        for rel in self.relationships:
            if rel.source_id == tool_id and rel.relationship_type == "measures":
                indicator_ids.add(rel.target_id)

        return [self.indicators[ind_id] for ind_id in indicator_ids if ind_id in self.indicators]

    def get_indicators_for_dimension(self, dimension_id: str) -> List[Indicator]:
        """Get all indicators in a specific dimension."""
        indicator_ids = set()
        for rel in self.relationships:
            if rel.source_id == dimension_id and rel.relationship_type == "contains":
                indicator_ids.add(rel.target_id)

        return [self.indicators[ind_id] for ind_id in indicator_ids if ind_id in self.indicators]

    def validate_relationships(self) -> Tuple[int, List[str]]:
        """
        Validate relationship integrity.

        Returns:
            Tuple of (valid_count, error_list)
        """
        logger.info("Validating relationships...")

        valid_count = 0
        errors = []

        for rel in self.relationships:
            # Check source exists
            if rel.source_type == "Indicator" and rel.source_id not in self.indicators:
                errors.append(f"Relationship references unknown indicator {rel.source_id}")
                continue
            if rel.source_type == "Tool" and rel.source_id not in self.tools:
                errors.append(f"Relationship references unknown tool {rel.source_id}")
                continue
            if rel.source_type == "Dimension" and rel.source_id not in self.dimensions:
                errors.append(f"Relationship references unknown dimension {rel.source_id}")
                continue

            # Check target exists
            if rel.target_type == "Indicator" and rel.target_id not in self.indicators:
                errors.append(f"Relationship references unknown indicator {rel.target_id}")
                continue
            if rel.target_type == "Tool" and rel.target_id not in self.tools:
                errors.append(f"Relationship references unknown tool {rel.target_id}")
                continue
            if rel.target_type == "Dimension" and rel.target_id not in self.dimensions:
                errors.append(f"Relationship references unknown dimension {rel.target_id}")
                continue

            valid_count += 1

        logger.info(f"Validated {valid_count} relationships")
        if errors:
            logger.warning(f"Found {len(errors)} validation errors")

        return valid_count, errors

    def save_to_cache(self) -> Path:
        """
        Save relationships to cache file.

        Returns:
            Path to the cache file
        """
        from pathlib import Path

        cache_file = Path(CACHE_DIR) / "relationships.json"

        data = {
            "type": "RelationshipGraph",
            "edges": [rel.model_dump() for rel in self.relationships],
            "node_counts": {
                "indicators": len(self.indicators),
                "tools": len(self.tools),
                "dimensions": len(self.dimensions),
            },
            "edge_count": len(self.relationships),
        }

        save_json(data, cache_file)
        return cache_file

    def export_graph(self) -> Dict:
        """
        Export graph as dictionary for API generation.

        Returns:
            Graph data structure
        """
        return {
            "type": "RelationshipGraph",
            "nodes": {
                "indicators": {id: ind.model_dump(mode="json") for id, ind in self.indicators.items()},
                "tools": {id: tool.model_dump(mode="json") for id, tool in self.tools.items()},
                "dimensions": {id: dim.model_dump(mode="json") for id, dim in self.dimensions.items()},
            },
            "edges": [rel.model_dump(mode="json") for rel in self.relationships],
            "statistics": {
                "total_indicators": len(self.indicators),
                "total_tools": len(self.tools),
                "total_dimensions": len(self.dimensions),
                "total_relationships": len(self.relationships),
            },
        }
