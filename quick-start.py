#!/usr/bin/env python3
"""Quick start example - Using the EVERSE Unified API locally."""

import json
from pathlib import Path

# Import scripts (adjust path as needed)
import sys

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from fetch_indicators import fetch_and_validate_indicators
from fetch_tools import fetch_and_validate_tools
from fetch_dimensions import fetch_and_validate_dimensions
from build_relationships import RelationshipBuilder


def main():
    """Run quick start example."""
    print("=" * 60)
    print("EVERSE Unified API - Quick Start")
    print("=" * 60)

    # Fetch data
    print("\n1. Fetching data...")
    indicators = fetch_and_validate_indicators(use_cache=True)
    tools = fetch_and_validate_tools(use_cache=True)
    dimensions = fetch_and_validate_dimensions(use_cache=True)

    print(f"   ✓ {len(indicators)} indicators")
    print(f"   ✓ {len(tools)} tools")
    print(f"   ✓ {len(dimensions)} dimensions")

    # Build relationships
    print("\n2. Building relationships...")
    builder = RelationshipBuilder()
    builder.add_indicators(indicators)
    builder.add_tools(tools)
    builder.add_dimensions(dimensions)
    builder.build_all_relationships()

    print(f"   ✓ {len(builder.relationships)} relationships")

    # Show examples
    print("\n3. Example queries:")

    # Find tools for a specific indicator
    if indicators:
        indicator = indicators[0]
        tools_for_ind = builder.get_tools_for_indicator(indicator.id)
        print(f"\n   Tools for '{indicator.name}' ({indicator.id}):")
        if tools_for_ind:
            for tool in tools_for_ind[:3]:
                print(f"   - {tool.name} ({tool.ring})")
        else:
            print("   - No tools found")

    # Find indicators for a dimension
    if dimensions:
        dimension = dimensions[0]
        inds_for_dim = builder.get_indicators_for_dimension(dimension.id)
        print(f"\n   Indicators in '{dimension.name}' ({dimension.id}):")
        if inds_for_dim:
            for ind in inds_for_dim[:3]:
                print(f"   - {ind.name}")
        else:
            print("   - No indicators found")

    # Show some statistics
    print("\n4. Statistics:")
    print(f"   Total indicators: {len(indicators)}")
    print(f"   Total tools: {len(tools)}")
    print(f"   Total dimensions: {len(dimensions)}")
    print(f"   Total relationships: {len(builder.relationships)}")

    # Validate
    valid, errors = builder.validate_relationships()
    print(f"   Valid relationships: {valid}")
    if errors:
        print(f"   Validation errors: {len(errors)}")

    print("\n" + "=" * 60)
    print("✓ Quick start complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: cd scripts && python generate_api.py")
    print("2. Check api/v1/ directory for generated endpoints")
    print("3. Review docs/api-reference.md for API documentation")


if __name__ == "__main__":
    main()
