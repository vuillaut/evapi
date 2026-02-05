"""Common utilities for EVERSE Unified API."""

import json
import logging
import time
from typing import Any, Dict, List, Optional
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from scripts.config import GITHUB_TOKEN, HTTP_TIMEOUT, MAX_RETRIES, RETRY_BACKOFF

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_session_with_retries() -> requests.Session:
    """Create a requests session with automatic retries."""
    session = requests.Session()

    # Configure retries
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD", "OPTIONS"],
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Add authorization if GitHub token is available
    if GITHUB_TOKEN:
        session.headers.update({"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3.raw"})

    return session


def fetch_json(url: str, timeout: int = HTTP_TIMEOUT) -> Optional[Dict[str, Any]]:
    """
    Fetch JSON data from a URL with retry logic.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON data or None if fetch fails
    """
    session = get_session_with_retries()

    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None
    finally:
        session.close()


import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from scripts.models import Indicator, Tool, Dimension

logger = logging.getLogger(__name__)


class PydanticJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Pydantic models and HttpUrl objects."""

    def default(self, obj):
        # Handle Pydantic models
        if hasattr(obj, "model_dump"):
            return obj.model_dump(mode="json", exclude={"metadata"})

        # Handle HttpUrl objects
        if hasattr(obj, "__class__") and "HttpUrl" in str(obj.__class__):
            return str(obj)

        # Handle other objects
        return super().default(obj)


def convert_httpurl_to_str(obj):
    """Recursively convert HttpUrl objects and Pydantic models to strings in nested data structures."""
    if hasattr(obj, "__class__") and "HttpUrl" in str(obj.__class__):
        return str(obj)
    elif hasattr(obj, "model_dump"):
        # Convert Pydantic model to dict, excluding metadata
        model_dict = obj.model_dump(exclude={"metadata"})
        # Recursively process the dict
        return {key: convert_httpurl_to_str(value) for key, value in model_dict.items()}
    elif isinstance(obj, dict):
        return {key: convert_httpurl_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_httpurl_to_str(item) for item in obj]
    else:
        return obj


def save_json(data, filepath: Path) -> None:
    """
    Save data to a JSON file.

    Args:
        data: Data to save (dict, list, or Pydantic models)
        filepath: Path to save the file
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Recursively convert any HttpUrl objects and Pydantic models to serializable format
    data = convert_httpurl_to_str(data)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved JSON to {filepath}")


def load_json(filepath: Path) -> Optional[Dict[str, Any]]:
    """
    Load JSON from a file.

    Args:
        filepath: Path to the file

    Returns:
        Parsed JSON data or None if file doesn't exist
    """
    if not filepath.exists():
        logger.warning(f"File not found: {filepath}")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {filepath}: {e}")
        return None


def list_github_files(owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
    """
    List files in a GitHub repository directory.

    Args:
        owner: Repository owner
        repo: Repository name
        path: Path within the repository

    Returns:
        List of file information dictionaries
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    session = get_session_with_retries()

    try:
        response = session.get(url, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to list GitHub files from {url}: {e}")
        return []
    finally:
        session.close()


def get_raw_github_url(owner: str, repo: str, path: str, branch: str = "main") -> str:
    """
    Get raw GitHub URL for a file.

    Args:
        owner: Repository owner
        repo: Repository name
        path: Path within the repository
        branch: Branch name

    Returns:
        Raw GitHub URL
    """
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
