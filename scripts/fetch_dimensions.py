"""Fetch dimensions from the EVERSE indicators repository."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from scripts.utils import fetch_json, list_github_files, get_raw_github_url, save_json, load_json
from scripts.models import Dimension
from scripts.config import CACHE_DIR

logger = logging.getLogger(__name__)

DIMENSIONS_OWNER = "EVERSE-ResearchSoftware"
DIMENSIONS_REPO = "indicators"
DIMENSIONS_PATH = "dimensions"


def fetch_dimensions_from_github() -> List[Dict]:
    """
    Fetch all dimension JSON files from the indicators repository.

    Returns:
        List of dimension data dictionaries
    """
    logger.info("Fetching dimensions from GitHub...")

    # List all files in the dimensions directory
    files = list_github_files(DIMENSIONS_OWNER, DIMENSIONS_REPO, DIMENSIONS_PATH)

    if not files:
        logger.error("Failed to list dimension files from GitHub")
        return []

    dimensions = []

    for file_info in files:
        if file_info.get("name", "").endswith(".json"):
            file_path = file_info.get("path", "")
            url = get_raw_github_url(DIMENSIONS_OWNER, DIMENSIONS_REPO, file_path)

            logger.info(f"Fetching dimension: {file_info['name']}")
            dimension_data = fetch_json(url)

            if dimension_data:
                dimensions.append(dimension_data)
            else:
                logger.warning(f"Failed to fetch {file_info['name']}")

    logger.info(f"Successfully fetched {len(dimensions)} dimensions")
    return dimensions


def validate_dimensions(dimensions: List[Dict]) -> List[Dimension]:
    """
    Validate dimensions against the Dimension model.

    Args:
        dimensions: List of raw dimension data

    Returns:
        List of validated Dimension objects
    """
    logger.info(f"Validating {len(dimensions)} dimensions...")

    validated = []
    errors = []

    for dimension_data in dimensions:
        try:
            # Extract required fields - handle JSON-LD @id field
            dimension_id = dimension_data.get("id") or dimension_data.get("@id")
            name = dimension_data.get("name")

            if not dimension_id or not name:
                logger.warning(f"Skipping dimension without id or name: {dimension_data}")
                continue

            # Create Dimension model
            dimension = Dimension(
                id=dimension_id,
                name=name,
                description=dimension_data.get("description"),
                indicators=dimension_data.get("indicators", []),
                metadata=dimension_data,
            )
            validated.append(dimension)

        except Exception as e:
            error_msg = f"Validation error for dimension {dimension_data.get('id', 'unknown')}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

    if errors:
        logger.warning(f"Found {len(errors)} validation errors")

    logger.info(f"Successfully validated {len(validated)} dimensions")
    return validated


def save_dimensions_cache(dimensions: List[Dimension]) -> Path:
    """
    Save dimensions to cache file.

    Args:
        dimensions: List of validated dimensions

    Returns:
        Path to the cache file
    """
    cache_file = CACHE_DIR / "dimensions.json"

    data = {
        "type": "DimensionCollection",
        "items": [dimension.model_dump() for dimension in dimensions],
        "count": len(dimensions),
    }

    save_json(data, cache_file)
    return cache_file


def load_dimensions_cache() -> Optional[List[Dimension]]:
    """
    Load dimensions from cache file.

    Returns:
        List of dimensions or None if cache doesn't exist
    """
    cache_file = CACHE_DIR / "dimensions.json"

    data = load_json(cache_file)
    if not data:
        return None

    try:
        items = data.get("items", [])
        return [Dimension(**item) for item in items]
    except Exception as e:
        logger.error(f"Failed to load dimensions cache: {e}")
        return None


def fetch_and_validate_dimensions(use_cache: bool = True) -> List[Dimension]:
    """
    Fetch and validate dimensions.

    Args:
        use_cache: Whether to try loading from cache first

    Returns:
        List of validated dimensions
    """
    if use_cache:
        cached = load_dimensions_cache()
        if cached:
            logger.info(f"Loaded {len(cached)} dimensions from cache")
            return cached

    raw_dimensions = fetch_dimensions_from_github()
    validated = validate_dimensions(raw_dimensions)

    if validated:
        save_dimensions_cache(validated)

    return validated
