"""Validate API data and structure."""

import logging
from pathlib import Path
from typing import List, Tuple

from jsonschema import validate, ValidationError
from scripts.models import Indicator, Tool, Dimension

logger = logging.getLogger(__name__)


def validate_indicator(indicator: Indicator) -> Tuple[bool, List[str]]:
    """
    Validate an indicator.

    Args:
        indicator: Indicator to validate

    Returns:
        Tuple of (is_valid, error_list)
    """
    errors = []

    # Check required fields
    if not indicator.id:
        errors.append("Indicator missing required field: id")
    if not indicator.name:
        errors.append("Indicator missing required field: name")

    # Check ID format (should be lowercase, alphanumeric with hyphens, or a valid URL)
    if indicator.id:
        # Allow URLs or simple identifiers
        is_url = indicator.id.startswith(("http://", "https://"))
        is_simple_id = all(c.isalnum() or c in "-_" for c in indicator.id)
        if not (is_url or is_simple_id):
            errors.append(f"Indicator ID has invalid format: {indicator.id}")

    return len(errors) == 0, errors


def validate_tool(tool: Tool) -> Tuple[bool, List[str]]:
    """
    Validate a tool.

    Args:
        tool: Tool to validate

    Returns:
        Tuple of (is_valid, error_list)
    """
    errors = []

    # Check required fields
    if not tool.id:
        errors.append("Tool missing required field: id")
    if not tool.name:
        errors.append("Tool missing required field: name")

    # Check ring value
    if tool.ring:
        valid_rings = {"adopt", "trial", "assess", "hold"}
        if tool.ring.lower() not in valid_rings:
            errors.append(f"Tool has invalid ring: {tool.ring}")

    return len(errors) == 0, errors


def validate_dimension(dimension: Dimension) -> Tuple[bool, List[str]]:
    """
    Validate a dimension.

    Args:
        dimension: Dimension to validate

    Returns:
        Tuple of (is_valid, error_list)
    """
    errors = []

    # Check required fields
    if not dimension.id:
        errors.append("Dimension missing required field: id")
    if not dimension.name:
        errors.append("Dimension missing required field: name")

    return len(errors) == 0, errors


def validate_collections(
    indicators: List[Indicator],
    tools: List[Tool],
    dimensions: List[Dimension],
) -> Tuple[bool, List[str]]:
    """
    Validate collections of entities.

    Args:
        indicators: List of indicators
        tools: List of tools
        dimensions: List of dimensions

    Returns:
        Tuple of (is_valid, error_list)
    """
    errors = []
    logger.info("Validating entity collections...")

    # Validate individual items
    for indicator in indicators:
        valid, ind_errors = validate_indicator(indicator)
        if not valid:
            errors.extend(ind_errors)

    for tool in tools:
        valid, tool_errors = validate_tool(tool)
        if not valid:
            errors.extend(tool_errors)

    for dimension in dimensions:
        valid, dim_errors = validate_dimension(dimension)
        if not valid:
            errors.extend(dim_errors)

    logger.info(f"Validated {len(indicators)} indicators, {len(tools)} tools, {len(dimensions)} dimensions")

    if errors:
        logger.warning(f"Found {len(errors)} validation errors")
    else:
        logger.info("All validations passed")

    return len(errors) == 0, errors


def validate_api_files(api_dir: Path) -> Tuple[bool, List[str]]:
    """
    Validate generated API files structure.

    Args:
        api_dir: Path to API directory

    Returns:
        Tuple of (is_valid, error_list)
    """
    errors = []
    logger.info(f"Validating API files in {api_dir}...")

    required_files = [
        "index.json",
        "indicators/index.json",
        "tools/index.json",
        "dimensions/index.json",
        "relationships/graph.json",
    ]

    for file_path in required_files:
        full_path = api_dir / file_path
        if not full_path.exists():
            errors.append(f"Missing required API file: {file_path}")
        else:
            logger.info(f"✓ {file_path}")

    if errors:
        logger.warning(f"Found {len(errors)} missing files")
    else:
        logger.info("All required files present")

    return len(errors) == 0, errors
