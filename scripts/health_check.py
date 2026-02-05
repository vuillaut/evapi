"""Health check and status endpoint generator for EVERSE Unified API."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.config import API_DIR, API_VERSION


def get_api_stats() -> Dict[str, Any]:
    """Get statistics about the generated API."""
    api_dir = API_DIR

    stats = {
        "indicators": 0,
        "tools": 0,
        "dimensions": 0,
        "has_openapi": False,
        "has_relationships": False,
    }

    # Count indicators
    indicators_dir = api_dir / "indicators"
    if indicators_dir.exists():
        json_files = list(indicators_dir.glob("*.json"))
        # Subtract index.json if it exists
        stats["indicators"] = len([f for f in json_files if f.name != "index.json"])

    # Count tools
    tools_dir = api_dir / "tools"
    if tools_dir.exists():
        json_files = list(tools_dir.glob("*.json"))
        # Subtract index.json and index_p*.json
        stats["tools"] = len([f for f in json_files if not f.name.startswith("index")])

    # Count dimensions
    dimensions_dir = api_dir / "dimensions"
    if dimensions_dir.exists():
        json_files = list(dimensions_dir.glob("*.json"))
        # Subtract index.json
        stats["dimensions"] = len([f for f in json_files if f.name != "index.json"])

    # Check for OpenAPI spec
    stats["has_openapi"] = (api_dir / "openapi.json").exists()

    # Check for relationships
    stats["has_relationships"] = (api_dir / "relationships" / "graph.json").exists()

    return stats


def generate_health_endpoint() -> None:
    """Generate the health check endpoint."""
    stats = get_api_stats()

    health_data = {
        "@context": "https://www.w3.org/2019/wot/td/v1",
        "@type": "HealthCheck",
        "name": "EVERSE Unified API Health",
        "description": "Health status and metrics for the EVERSE Unified API",
        "version": API_VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "healthy",
        "components": {
            "api": {
                "status": "healthy",
                "endpoints": {
                    "root": f"/api/v1/index.json",
                    "indicators": f"/api/v1/indicators/index.json",
                    "tools": f"/api/v1/tools/index.json",
                    "dimensions": f"/api/v1/dimensions/index.json",
                    "openapi": f"/api/v1/openapi.json",
                    "relationships": f"/api/v1/relationships/graph.json",
                },
            },
            "data": {
                "status": "healthy",
                "indicators": stats["indicators"],
                "tools": stats["tools"],
                "dimensions": stats["dimensions"],
            },
            "openapi": {
                "status": "healthy" if stats["has_openapi"] else "missing",
                "available": stats["has_openapi"],
            },
            "relationships": {
                "status": "healthy" if stats["has_relationships"] else "empty",
                "available": stats["has_relationships"],
            },
        },
        "metrics": {
            "total_endpoints": 3 + stats["indicators"] + stats["tools"] + stats["dimensions"],
            "pagination": True,
            "hateoas": True,
            "json_ld": True,
            "openapi_3_0": stats["has_openapi"],
        },
        "_links": {
            "self": "/api/v1/health.json",
            "api": "/api/v1/index.json",
            "docs": "/api/v1/openapi.json",
        },
    }

    # Ensure directory exists
    (API_DIR).mkdir(parents=True, exist_ok=True)

    # Write health endpoint
    health_file = API_DIR / "health.json"
    with open(health_file, "w", encoding="utf-8") as f:
        json.dump(health_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Generated health endpoint: {health_file}")


def generate_status_endpoint() -> None:
    """Generate the deployment status endpoint."""
    status_data = {
        "@context": "https://www.w3.org/2019/wot/td/v1",
        "@type": "Status",
        "name": "EVERSE Unified API Status",
        "description": "Current deployment status and information",
        "version": API_VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "deployment": {
            "status": "active",
            "environment": "production",
            "last_update": datetime.utcnow().isoformat() + "Z",
            "update_frequency": "every 6 hours",
            "update_trigger": "scheduled + manual + push",
        },
        "uptime": {
            "status": "monitoring",
            "service": "GitHub Pages",
            "region": "global",
        },
        "support": {
            "issues": "https://github.com/vuillaut/evapi/issues",
            "discussions": "https://github.com/vuillaut/evapi/discussions",
            "documentation": "/api/v1/openapi.json",
        },
        "_links": {
            "self": "/api/v1/status.json",
            "health": "/api/v1/health.json",
            "api": "/api/v1/index.json",
        },
    }

    # Ensure directory exists
    (API_DIR).mkdir(parents=True, exist_ok=True)

    # Write status endpoint
    status_file = API_DIR / "status.json"
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Generated status endpoint: {status_file}")


def generate_dashboard() -> None:
    """Generate monitoring dashboard HTML."""
    dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EVERSE Unified API - Status Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #f0f0f0;
            padding-bottom: 10px;
        }
        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
            margin: 5px 0;
        }
        .healthy {
            background: #d4edda;
            color: #155724;
        }
        .degraded {
            background: #fff3cd;
            color: #856404;
        }
        .unhealthy {
            background: #f8d7da;
            color: #721c24;
        }
        .metric-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .metric-row:last-child {
            border-bottom: none;
        }
        .metric-label {
            color: #666;
            font-weight: 500;
        }
        .metric-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .feature-list {
            list-style: none;
        }
        .feature-list li {
            padding: 8px 0;
            display: flex;
            align-items: center;
        }
        .feature-list li::before {
            content: "✅";
            margin-right: 10px;
            font-size: 1.2em;
        }
        .feature-list li.disabled::before {
            content: "❌";
        }
        footer {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .timestamp {
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #d32f2f;
        }
        .links {
            margin-top: 15px;
        }
        .links a {
            color: #667eea;
            text-decoration: none;
            margin: 0 10px;
            font-weight: 500;
        }
        .links a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 EVERSE Unified API</h1>
            <p class="subtitle">Real-time Status Dashboard</p>
            <div class="links">
                <a href="./index.json">API Root</a> •
                <a href="./openapi.json">OpenAPI Spec</a> •
                <a href="https://github.com/vuillaut/evapi">GitHub</a>
            </div>
        </header>

        <div class="status-grid">
            <div class="card">
                <h2>🏥 API Health</h2>
                <div id="health-content" class="loading">
                    <div class="spinner"></div>
                    Loading health status...
                </div>
            </div>

            <div class="card">
                <h2>📊 API Metrics</h2>
                <div id="metrics-content" class="loading">
                    <div class="spinner"></div>
                    Loading metrics...
                </div>
            </div>

            <div class="card">
                <h2>🔧 Components</h2>
                <div id="components-content" class="loading">
                    <div class="spinner"></div>
                    Loading components...
                </div>
            </div>

            <div class="card">
                <h2>✨ Features</h2>
                <div id="features-content" class="loading">
                    <div class="spinner"></div>
                    Loading features...
                </div>
            </div>
        </div>

        <footer>
            <p>Monitoring powered by GitHub Pages</p>
            <p class="timestamp">Last updated: <span id="last-update">Loading...</span></p>
        </footer>
    </div>

    <script>
        async function loadHealth() {
            try {
                const response = await fetch('./health.json');
                if (!response.ok) throw new Error('Failed to fetch health');
                
                const data = await response.json();
                const statusClass = data.status === 'healthy' ? 'healthy' : 
                                  data.status === 'degraded' ? 'degraded' : 'unhealthy';
                
                document.getElementById('health-content').innerHTML = `
                    <div style="text-align: center; padding: 20px 0;">
                        <div class="status-badge ${statusClass}" style="font-size: 1.2em;">
                            ${data.status.toUpperCase()}
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Version</span>
                            <span class="metric-value" style="font-size: 1.2em;">${data.version}</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">API Status</span>
                            <span class="metric-value" style="font-size: 1.2em;">${data.components.api}</span>
                        </div>
                    </div>
                `;

                // Update components
                document.getElementById('components-content').innerHTML = `
                    <div class="metric-row">
                        <span class="metric-label">API Core</span>
                        <span class="status-badge ${data.components.api === 'healthy' ? 'healthy' : 'unhealthy'}">
                            ${data.components.api}
                        </span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Data Sources</span>
                        <span class="status-badge ${data.components.data_sources === 'healthy' ? 'healthy' : 'unhealthy'}">
                            ${data.components.data_sources}
                        </span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Relationships</span>
                        <span class="status-badge ${data.components.relationships === 'healthy' ? 'healthy' : 'unhealthy'}">
                            ${data.components.relationships}
                        </span>
                    </div>
                `;

                document.getElementById('last-update').textContent = 
                    new Date(data.timestamp).toLocaleString();
                    
            } catch (error) {
                document.getElementById('health-content').innerHTML = 
                    `<div class="error">❌ Failed to load health status<br><small>${error.message}</small></div>`;
            }
        }

        async function loadStatus() {
            try {
                const response = await fetch('./status.json');
                if (!response.ok) throw new Error('Failed to fetch status');
                
                const data = await response.json();

                // Update metrics
                document.getElementById('metrics-content').innerHTML = `
                    <div class="metric-row">
                        <span class="metric-label">Indicators</span>
                        <span class="metric-value">${data.metrics.indicators}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Tools</span>
                        <span class="metric-value">${data.metrics.tools}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Dimensions</span>
                        <span class="metric-value">${data.metrics.dimensions}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Relationships</span>
                        <span class="metric-value">${data.metrics.relationships}</span>
                    </div>
                `;

                // Update features
                if (data.features) {
                    const featuresList = Object.entries(data.features)
                        .map(([key, value]) => {
                            const className = value ? '' : 'disabled';
                            const label = key.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                            return `<li class="${className}">${label}</li>`;
                        })
                        .join('');
                    
                    document.getElementById('features-content').innerHTML = 
                        `<ul class="feature-list">${featuresList}</ul>`;
                } else {
                    document.getElementById('features-content').innerHTML = 
                        '<p style="color: #999; text-align: center;">No feature data available</p>';
                }

            } catch (error) {
                document.getElementById('metrics-content').innerHTML = 
                    `<div class="error">❌ Failed to load metrics<br><small>${error.message}</small></div>`;
            }
        }

        // Load data on page load
        loadHealth();
        loadStatus();

        // Refresh every minute
        setInterval(() => {
            loadHealth();
            loadStatus();
        }, 60000);
    </script>
</body>
</html>"""

    # Ensure directory exists
    (API_DIR).mkdir(parents=True, exist_ok=True)

    # Write dashboard HTML
    dashboard_file = API_DIR / "dashboard.html"
    with open(dashboard_file, "w", encoding="utf-8") as f:
        f.write(dashboard_html)

    print(f"✓ Generated monitoring dashboard: {dashboard_file}")


if __name__ == "__main__":
    print("Generating health check and status endpoints...")
    generate_health_endpoint()
    generate_status_endpoint()
    generate_dashboard()
    print("✓ Health check endpoints generated successfully!")
