"""Fetch indicators from the EVERSE indicators repository."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from scripts.utils import fetch_json, list_github_files, get_raw_github_url, save_json, load_json
from scripts.models import Indicator
from scripts.config import CACHE_DIR

logger = logging.getLogger(__name__)

INDICATORS_OWNER = "EVERSE-ResearchSoftware"
INDICATORS_REPO = "indicators"
INDICATORS_PATH = "indicators"


def fetch_indicators_from_github() -> List[Dict]:
    """
    Fetch all indicator JSON files from the indicators repository.

    Returns:
        List of indicator data dictionaries
    """
    logger.info("Fetching indicators from GitHub...")

    # List all files in the indicators directory
    files = list_github_files(INDICATORS_OWNER, INDICATORS_REPO, INDICATORS_PATH)

    if not files:
        logger.error("Failed to list indicator files from GitHub")
        return []

    indicators = []

    for file_info in files:
        if file_info.get("name", "").endswith(".json"):
            file_path = file_info.get("path", "")
            url = get_raw_github_url(INDICATORS_OWNER, INDICATORS_REPO, file_path)

            logger.info(f"Fetching indicator: {file_info['name']}")
            indicator_data = fetch_json(url)

            if indicator_data:
                indicators.append(indicator_data)
            else:
                logger.warning(f"Failed to fetch {file_info['name']}")

    logger.info(f"Successfully fetched {len(indicators)} indicators")
    return indicators


def validate_indicators(indicators: List[Dict]) -> List[Indicator]:
    """
    Validate indicators against the Indicator model.

    Args:
        indicators: List of raw indicator data

    Returns:
        List of validated Indicator objects
    """
    logger.info(f"Validating {len(indicators)} indicators...")

    validated = []
    errors = []

    for indicator_data in indicators:
        try:
            # Extract required fields - handle JSON-LD @id field
            indicator_id = indicator_data.get("id") or indicator_data.get("@id")
            name = indicator_data.get("name")

            if not indicator_id or not name:
                logger.warning(f"Skipping indicator without id or name: {indicator_data}")
                continue

            # Create Indicator model
            indicator = Indicator(
                id=indicator_id,
                name=name,
                description=indicator_data.get("description"),
                dimension=indicator_data.get("dimension"),
                category=indicator_data.get("category"),
                rationale=indicator_data.get("rationale"),
                url=indicator_data.get("url"),
                related_tools=indicator_data.get("related_tools", []),
                metadata=indicator_data,
            )
            validated.append(indicator)

        except Exception as e:
            error_msg = f"Validation error for indicator {indicator_data.get('id', 'unknown')}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

    if errors:
        logger.warning(f"Found {len(errors)} validation errors")

    logger.info(f"Successfully validated {len(validated)} indicators")
    return validated


def save_indicators_cache(indicators: List[Indicator]) -> Path:
    """
    Save indicators to cache file.

    Args:
        indicators: List of validated indicators

    Returns:
        Path to the cache file
    """
    cache_file = CACHE_DIR / "indicators.json"

    data = {
        "type": "IndicatorCollection",
        "items": [indicator.model_dump() for indicator in indicators],
        "count": len(indicators),
    }

    save_json(data, cache_file)
    return cache_file


def load_indicators_cache() -> Optional[List[Indicator]]:
    """
    Load indicators from cache file.

    Returns:
        List of indicators or None if cache doesn't exist
    """
    from pathlib import Path

    cache_file = Path(CACHE_DIR) / "indicators.json"

    data = load_json(cache_file)
    if not data:
        return None

    try:
        items = data.get("items", [])
        return [Indicator(**item) for item in items]
    except Exception as e:
        logger.error(f"Failed to load indicators cache: {e}")
        return None


def fetch_and_validate_indicators(use_cache: bool = True) -> List[Indicator]:
    """
    Fetch and validate indicators.

    Args:
        use_cache: Whether to try loading from cache first

    Returns:
        List of validated indicators
    """
    if use_cache:
        cached = load_indicators_cache()
        if cached:
            logger.info(f"Loaded {len(cached)} indicators from cache")
            return cached

    raw_indicators = fetch_indicators_from_github()
    validated = validate_indicators(raw_indicators)

    if validated:
        save_indicators_cache(validated)

    return validated
