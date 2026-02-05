"""Deployment validation script for EVERSE Unified API."""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from urllib.parse import urljoin
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.config import API_DIR, API_BASE_URL


class DeploymentValidator:
    """Validates the generated API deployment."""

    def __init__(self, api_dir: Path = API_DIR, base_url: str = API_BASE_URL):
        self.api_dir = api_dir
        self.base_url = base_url
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating EVERSE Unified API deployment...\n")

        checks = [
            ("API Structure", self.check_api_structure),
            ("Required Endpoints", self.check_required_endpoints),
            ("HATEOAS Links", self.check_hateoas_links),
            ("JSON-LD Context", self.check_json_ld_context),
            ("OpenAPI Specification", self.check_openapi_spec),
            ("Data Integrity", self.check_data_integrity),
            ("Link Integrity", self.check_link_integrity),
        ]

        for check_name, check_func in checks:
            print(f"▶ {check_name}...")
            try:
                check_func()
            except Exception as e:
                self.errors.append(f"{check_name}: {str(e)}")

        self.print_results()
        return len(self.errors) == 0

    def check_api_structure(self) -> None:
        """Check if API directory structure exists."""
        required_dirs = [
            self.api_dir,
            self.api_dir / "indicators",
            self.api_dir / "tools",
            self.api_dir / "dimensions",
            self.api_dir / "relationships",
        ]

        for dir_path in required_dirs:
            if not dir_path.exists():
                self.errors.append(f"Missing directory: {dir_path}")
            else:
                self.passed.append(f"Directory exists: {dir_path.name}")

    def check_required_endpoints(self) -> None:
        """Check if required endpoint files exist."""
        required_files = [
            "index.json",
            "indicators/index.json",
            "tools/index.json",
            "dimensions/index.json",
            "openapi.json",
            "relationships/graph.json",
            "health.json",
            "status.json",
        ]

        for file_path in required_files:
            full_path = self.api_dir / file_path
            if not full_path.exists():
                self.errors.append(f"Missing endpoint: {file_path}")
            else:
                self.passed.append(f"Endpoint exists: {file_path}")

    def check_hateoas_links(self) -> None:
        """Check HATEOAS links in responses."""
        # Check a few sample files
        samples = [
            "index.json",
            "indicators/index.json",
            "tools/index.json",
        ]

        link_count = 0
        for sample in samples:
            file_path = self.api_dir / sample
            if file_path.exists():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)

                    if "_links" in data:
                        links = data["_links"]
                        link_count += len(links)
                    else:
                        self.warnings.append(f"No _links in {sample}")
                except json.JSONDecodeError as e:
                    self.errors.append(f"Invalid JSON in {sample}: {str(e)}")

        if link_count > 0:
            self.passed.append(f"Found {link_count} HATEOAS links")
        else:
            self.errors.append("No HATEOAS links found")

    def check_json_ld_context(self) -> None:
        """Check JSON-LD context in responses."""
        # Check root endpoint
        file_path = self.api_dir / "index.json"
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                if "@context" in data:
                    self.passed.append("JSON-LD context found in root")
                else:
                    self.errors.append("Missing @context in root endpoint")
            except json.JSONDecodeError as e:
                self.errors.append(f"Invalid JSON in root: {str(e)}")

    def check_openapi_spec(self) -> None:
        """Check OpenAPI specification."""
        file_path = self.api_dir / "openapi.json"
        if not file_path.exists():
            self.errors.append("OpenAPI specification not found")
            return

        try:
            with open(file_path, encoding="utf-8") as f:
                spec = json.load(f)

            # Check basic structure
            required_fields = ["openapi", "info", "paths"]
            missing_fields = [f for f in required_fields if f not in spec]

            if missing_fields:
                self.errors.append(f"Missing OpenAPI fields: {missing_fields}")
            else:
                self.passed.append(f"OpenAPI spec valid with {len(spec.get('paths', {}))} paths")

            # Check OpenAPI version
            openapi_version = spec.get("openapi", "")
            if openapi_version.startswith("3."):
                self.passed.append(f"Using OpenAPI {openapi_version}")
            else:
                self.errors.append(f"Unexpected OpenAPI version: {openapi_version}")

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid OpenAPI JSON: {str(e)}")

    def check_data_integrity(self) -> None:
        """Check data integrity in generated files."""
        # Count entities
        indicators_count = self._count_entity_files("indicators")
        tools_count = self._count_entity_files("tools")
        dimensions_count = self._count_entity_files("dimensions")

        self.passed.append(f"Found {indicators_count} indicators")
        self.passed.append(f"Found {tools_count} tools")
        self.passed.append(f"Found {dimensions_count} dimensions")

        # Check minimum requirements
        if indicators_count == 0:
            self.errors.append("No indicators found")
        if tools_count == 0:
            self.errors.append("No tools found")
        if dimensions_count == 0:
            self.errors.append("No dimensions found")

    def check_link_integrity(self) -> None:
        """Check that links in responses are properly formatted."""
        # Sample indicators collection
        file_path = self.api_dir / "indicators" / "index.json"
        if not file_path.exists():
            self.warnings.append("Cannot check link integrity: indicators index not found")
            return

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            broken_links = []
            items = data.get("items", [])

            for item in items[:5]:  # Check first 5 items
                if "_links" in item:
                    for link_name, link_url in item["_links"].items():
                        if not self._is_valid_link(link_url):
                            broken_links.append(f"{link_name}: {link_url}")

            if broken_links:
                self.errors.append(f"Invalid links found: {broken_links[:3]}")
            else:
                self.passed.append(f"Link format valid for sample items")

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in indicators: {str(e)}")

    @staticmethod
    def _is_valid_link(url: str) -> bool:
        """Check if a URL is valid."""
        # Check if it's a valid URL or relative path
        url_pattern = r"^(https?://|/)[^\s]+$"
        return bool(re.match(url_pattern, str(url)))

    def _count_entity_files(self, entity_type: str) -> int:
        """Count entity files in directory."""
        dir_path = self.api_dir / entity_type
        if not dir_path.exists():
            return 0

        json_files = list(dir_path.glob("*.json"))
        # Filter out index files
        entity_files = [f for f in json_files if not f.name.startswith("index")]
        return len(entity_files)

    def print_results(self) -> None:
        """Print validation results."""
        print("\n" + "=" * 70)

        if self.passed:
            print(f"\n✅ Passed ({len(self.passed)}):")
            for msg in self.passed:
                print(f"   • {msg}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for msg in self.warnings:
                print(f"   • {msg}")

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for msg in self.errors:
                print(f"   • {msg}")

        print("\n" + "=" * 70)

        if not self.errors:
            print("✅ All validation checks passed!")
            return_code = 0
        else:
            print(f"❌ {len(self.errors)} validation error(s) found")
            return_code = 1

        print("=" * 70 + "\n")
        return return_code


def main():
    """Run deployment validation."""
    validator = DeploymentValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
