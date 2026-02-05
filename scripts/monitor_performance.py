#!/usr/bin/env python3
"""Monitor API performance and response times."""

import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import requests
except ImportError:
    print("⚠️  requests module not available for remote monitoring")
    requests = None

BASE_URL = "https://vuillaut.github.io/evapi"

ENDPOINTS = [
    "/health.json",
    "/status.json",
    "/index.json",
    "/indicators/index.json",
    "/tools/index.json",
    "/dimensions/index.json",
    "/openapi.json",
    "/relationships/graph.json",
]


def check_endpoint_remote(endpoint: str) -> Dict:
    """Check endpoint response time and status via HTTP."""
    if not requests:
        return {
            "endpoint": endpoint,
            "status_code": 0,
            "response_time_ms": 0,
            "success": False,
            "error": "requests module not available",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    url = f"{BASE_URL}{endpoint}"
    start = time.time()

    try:
        response = requests.get(url, timeout=10)
        duration = (time.time() - start) * 1000  # ms

        return {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "response_time_ms": round(duration, 2),
            "success": response.status_code == 200,
            "content_length": len(response.content),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status_code": 0,
            "response_time_ms": 0,
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


def check_endpoint_local(endpoint: str) -> Dict:
    """Check endpoint by reading local files."""
    api_dir = Path(__file__).parent.parent / "api" / "v1"
    file_path = api_dir / endpoint.lstrip("/")

    start = time.time()

    try:
        if file_path.exists():
            content = file_path.read_text()
            duration = (time.time() - start) * 1000  # ms

            # Try to parse JSON to validate
            json.loads(content)

            return {
                "endpoint": endpoint,
                "status_code": 200,
                "response_time_ms": round(duration, 2),
                "success": True,
                "content_length": len(content),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        else:
            return {
                "endpoint": endpoint,
                "status_code": 404,
                "response_time_ms": 0,
                "success": False,
                "error": "File not found",
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status_code": 500,
            "response_time_ms": 0,
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


def format_size(bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB"]:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024
    return f"{bytes:.1f}GB"


def main(mode: str = "local"):
    """Run performance monitoring."""
    results = []

    print("🔍 Checking API Performance...")
    print(f"Mode: {mode.upper()}")
    if mode == "remote":
        print(f"Base URL: {BASE_URL}\n")
    else:
        print(f"API Directory: api/v1/\n")

    check_func = check_endpoint_remote if mode == "remote" else check_endpoint_local

    for endpoint in ENDPOINTS:
        result = check_func(endpoint)
        results.append(result)

        status = "✅" if result["success"] else "❌"
        size_info = f" ({format_size(result['content_length'])})" if "content_length" in result else ""
        error_info = f" - {result.get('error', '')}" if not result["success"] else ""
        print(f"{status} {endpoint}: {result['response_time_ms']}ms{size_info}{error_info}")

    # Calculate statistics
    successful = [r for r in results if r["success"]]
    if successful:
        avg_time = sum(r["response_time_ms"] for r in successful) / len(successful)
        max_time = max(r["response_time_ms"] for r in successful)
        min_time = min(r["response_time_ms"] for r in successful)
        total_size = sum(r.get("content_length", 0) for r in successful)

        print(f"\n📊 Statistics:")
        print(f"  Average Response Time: {avg_time:.2f}ms")
        print(f"  Min Response Time: {min_time:.2f}ms")
        print(f"  Max Response Time: {max_time:.2f}ms")
        print(f"  Total Content Size: {format_size(total_size)}")
        print(f"  Success Rate: {len(successful)}/{len(results)} ({len(successful) / len(results) * 100:.1f}%)")

        # Performance assessment
        if avg_time < 100:
            print(f"\n✅ Performance: EXCELLENT (avg < 100ms)")
        elif avg_time < 300:
            print(f"\n✅ Performance: GOOD (avg < 300ms)")
        elif avg_time < 500:
            print(f"\n⚠️  Performance: ACCEPTABLE (avg < 500ms)")
        else:
            print(f"\n❌ Performance: POOR (avg >= 500ms)")
    else:
        print("\n❌ No successful checks")
        avg_time = 0
        max_time = 0
        min_time = 0
        total_size = 0

    # Save results
    monitoring_dir = Path(__file__).parent.parent / "monitoring"
    monitoring_dir.mkdir(exist_ok=True)

    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = monitoring_dir / f"performance_{mode}_{timestamp_str}.json"

    with open(output_file, "w") as f:
        json.dump(
            {
                "mode": mode,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "base_url": BASE_URL if mode == "remote" else "local",
                "results": results,
                "statistics": {
                    "avg_response_time_ms": round(avg_time, 2) if successful else 0,
                    "max_response_time_ms": round(max_time, 2) if successful else 0,
                    "min_response_time_ms": round(min_time, 2) if successful else 0,
                    "total_size_bytes": total_size,
                    "success_rate": len(successful) / len(results) if results else 0,
                    "total_checks": len(results),
                    "successful_checks": len(successful),
                    "failed_checks": len(results) - len(successful),
                },
            },
            f,
            indent=2,
        )

    print(f"\n💾 Results saved to: {output_file}")

    # Exit with error if any checks failed
    if len(successful) < len(results):
        print(f"\n❌ {len(results) - len(successful)} checks failed")
        return 1

    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Monitor API performance")
    parser.add_argument(
        "--mode",
        choices=["local", "remote"],
        default="local",
        help="Monitoring mode: local (file system) or remote (HTTP)",
    )

    args = parser.parse_args()
    exit_code = main(args.mode)
    sys.exit(exit_code)
