"""Fetch tools from the EVERSE TechRadar repository."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from scripts.utils import fetch_json, list_github_files, get_raw_github_url, save_json, load_json
from scripts.models import Tool
from scripts.config import CACHE_DIR

logger = logging.getLogger(__name__)

TOOLS_OWNER = "EVERSE-ResearchSoftware"
TOOLS_REPO = "TechRadar"
TOOLS_PATH = "data/software-tools"


def fetch_tools_from_github() -> List[Dict]:
    """
    Fetch all tool JSON files from the TechRadar repository.

    Returns:
        List of tool data dictionaries
    """
    logger.info("Fetching tools from GitHub...")

    # List all files in the tools directory
    files = list_github_files(TOOLS_OWNER, TOOLS_REPO, TOOLS_PATH)

    if not files:
        logger.error("Failed to list tool files from GitHub")
        return []

    tools = []

    for file_info in files:
        if file_info.get("name", "").endswith(".json"):
            file_path = file_info.get("path", "")
            url = get_raw_github_url(TOOLS_OWNER, TOOLS_REPO, file_path)

            logger.info(f"Fetching tool: {file_info['name']}")
            tool_data = fetch_json(url)

            if tool_data:
                tools.append(tool_data)
            else:
                logger.warning(f"Failed to fetch {file_info['name']}")

    logger.info(f"Successfully fetched {len(tools)} tools")
    return tools


def validate_tools(tools: List[Dict]) -> List[Tool]:
    """
    Validate tools against the Tool model.

    Args:
        tools: List of raw tool data

    Returns:
        List of validated Tool objects
    """
    logger.info(f"Validating {len(tools)} tools...")

    validated = []
    errors = []

    for tool_data in tools:
        try:
            # Extract required fields - handle JSON-LD @id field
            tool_id = tool_data.get("id") or tool_data.get("@id")
            name = tool_data.get("name")

            if not tool_id or not name:
                logger.warning(f"Skipping tool without id or name: {tool_data}")
                continue

            # Create Tool model
            tool = Tool(
                id=tool_id,
                name=name,
                description=tool_data.get("description"),
                url=tool_data.get("url"),
                ring=tool_data.get("ring"),
                quadrant=tool_data.get("quadrant"),
                related_indicators=tool_data.get("related_indicators", []),
                metadata=tool_data,
            )
            validated.append(tool)

        except Exception as e:
            error_msg = f"Validation error for tool {tool_data.get('id', 'unknown')}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

    if errors:
        logger.warning(f"Found {len(errors)} validation errors")

    logger.info(f"Successfully validated {len(validated)} tools")
    return validated


def save_tools_cache(tools: List[Tool]) -> Path:
    """
    Save tools to cache file.

    Args:
        tools: List of validated tools

    Returns:
        Path to the cache file
    """
    cache_file = CACHE_DIR / "tools.json"

    data = {
        "type": "ToolCollection",
        "items": tools,  # Let save_json handle the conversion
        "count": len(tools),
    }

    save_json(data, cache_file)
    return cache_file


def load_tools_cache() -> Optional[List[Tool]]:
    """
    Load tools from cache file.

    Returns:
        List of tools or None if cache doesn't exist
    """
    from pathlib import Path

    cache_file = Path(CACHE_DIR) / "tools.json"

    data = load_json(cache_file)
    if not data:
        return None

    try:
        items = data.get("items", [])
        return [Tool(**item) for item in items]
    except Exception as e:
        logger.error(f"Failed to load tools cache: {e}")
        return None


def fetch_and_validate_tools(use_cache: bool = True) -> List[Tool]:
    """
    Fetch and validate tools.

    Args:
        use_cache: Whether to try loading from cache first

    Returns:
        List of validated tools
    """
    if use_cache:
        cached = load_tools_cache()
        if cached:
            logger.info(f"Loaded {len(cached)} tools from cache")
            return cached

    raw_tools = fetch_tools_from_github()
    validated = validate_tools(raw_tools)

    if validated:
        try:
            save_tools_cache(validated)
        except Exception as e:
            logger.warning(f"Failed to save tools cache: {e}. Continuing without cache.")

    return validated
