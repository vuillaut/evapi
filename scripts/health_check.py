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
                            <span class="metric-value" style="font-size: 1.2em;">${data.components.api.status}</span>
                        </div>
                    </div>
                `;

                // Update components
                const apiStatus = data.components.api.status === 'healthy' ? 'healthy' : 'unhealthy';
                const dataStatus = data.components.data.status === 'healthy' ? 'healthy' : 'unhealthy';
                const relStatus = data.components.relationships.status === 'healthy' ? 'healthy' : 'unhealthy';
                
                document.getElementById('components-content').innerHTML = `
                    <div class="metric-row">
                        <span class="metric-label">API Core</span>
                        <span class="status-badge ${apiStatus}">
                            ${data.components.api.status}
                        </span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Data Sources</span>
                        <span class="status-badge ${dataStatus}">
                            ${data.components.data.status}
                        </span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Relationships</span>
                        <span class="status-badge ${relStatus}">
                            ${data.components.relationships.status}
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
                const healthResponse = await fetch('./health.json');
                if (!healthResponse.ok) throw new Error('Failed to fetch health');
                const healthData = await healthResponse.json();

                // Update metrics from health.json
                document.getElementById('metrics-content').innerHTML = `
                    <div class="metric-row">
                        <span class="metric-label">Indicators</span>
                        <span class="metric-value">${healthData.components.data.indicators}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Tools</span>
                        <span class="metric-value">${healthData.components.data.tools}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Dimensions</span>
                        <span class="metric-value">${healthData.components.data.dimensions}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Total Endpoints</span>
                        <span class="metric-value">${healthData.metrics.total_endpoints}</span>
                    </div>
                `;

                // Update features
                const features = [
                    { name: 'Pagination', value: healthData.metrics.pagination },
                    { name: 'HATEOAS', value: healthData.metrics.hateoas },
                    { name: 'JSON-LD', value: healthData.metrics.json_ld },
                    { name: 'OpenAPI 3.0', value: healthData.metrics.openapi_3_0 }
                ];
                
                const featuresList = features
                    .map(f => {
                        const className = f.value ? '' : 'disabled';
                        return `<li class="${className}">✅ ${f.name}</li>`;
                    })
                    .join('');
                
                document.getElementById('features-content').innerHTML = 
                    `<ul class="feature-list">${featuresList}</ul>`;

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


def generate_landing_page() -> None:
    """Generate the main landing page/index."""
    stats = get_api_stats()

    landing_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EVERSE Unified API - Software Quality Services</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        nav {{
            background: white;
            padding: 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        nav ul {{
            list-style: none;
            display: flex;
            max-width: 1200px;
            margin: 0 auto;
            flex-wrap: wrap;
        }}
        
        nav li {{
            flex: 1;
            min-width: 150px;
        }}
        
        nav a {{
            display: block;
            padding: 15px 20px;
            color: #667eea;
            text-decoration: none;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }}
        
        nav a:hover {{
            background: #f0f0f0;
            border-bottom-color: #667eea;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }}
        
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .endpoints {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }}
        
        .endpoint-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .endpoint-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .endpoint-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.2em;
        }}
        
        .endpoint-card p {{
            color: #666;
            margin-bottom: 15px;
            font-size: 0.95em;
        }}
        
        .endpoint-link {{
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border-radius: 5px;
            text-decoration: none;
            transition: background 0.3s;
        }}
        
        .endpoint-link:hover {{
            background: #764ba2;
        }}
        
        .features {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            margin: 40px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .features h2 {{
            color: #667eea;
            margin-bottom: 20px;
        }}
        
        .features ul {{
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .features li {{
            padding: 10px;
            display: flex;
            align-items: center;
        }}
        
        .features li::before {{
            content: "✅";
            margin-right: 10px;
            font-size: 1.2em;
        }}
        
        .quick-start {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 8px;
            margin: 40px 0;
        }}
        
        .quick-start h2 {{
            margin-bottom: 20px;
        }}
        
        .code-block {{
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
        }}
        
        footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 30px;
            margin-top: 40px;
        }}
        
        footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        footer a:hover {{
            text-decoration: underline;
        }}
        
        .section-title {{
            color: #667eea;
            margin-top: 30px;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>🚀 EVERSE Unified API</h1>
        <p>Centralized API for EVERSE Research Software Quality Services</p>
    </header>
    
    <nav>
        <ul>
            <li><a href="#api">📡 API</a></li>
            <li><a href="#endpoints">📍 Endpoints</a></li>
            <li><a href="#features">⭐ Features</a></li>
            <li><a href="./dashboard.html">📊 Dashboard</a></li>
            <li><a href="./relationships/graph.html">🧭 Graph</a></li>
            <li><a href="./openapi.json" target="_blank">📖 OpenAPI Spec</a></li>
            <li><a href="https://github.com/vuillaut/evapi" target="_blank">💻 GitHub</a></li>
        </ul>
    </nav>
    
    <div class="container">
        <section id="overview">
            <div class="section-title">📊 API Overview</div>
            <p>
                The EVERSE Unified API provides seamless access to comprehensive research software quality data. 
                Aggregating indicators, tools, and dimensions from multiple authoritative sources, this API empowers 
                developers and organizations to assess and improve software quality systematically.
            </p>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>📈 Indicators</h3>
                    <div class="stat-number">{stats["indicators"]}</div>
                    <p>Quality indicators</p>
                </div>
                <div class="stat-card">
                    <h3>🔧 Tools</h3>
                    <div class="stat-number">{stats["tools"]}</div>
                    <p>Software tools</p>
                </div>
                <div class="stat-card">
                    <h3>📐 Dimensions</h3>
                    <div class="stat-number">{stats["dimensions"]}</div>
                    <p>Quality dimensions</p>
                </div>
            </div>
        </section>
        
        <section id="endpoints">
            <div class="section-title">📍 API Endpoints</div>
            
            <div class="endpoints">
                <div class="endpoint-card">
                    <h3>📈 Indicators</h3>
                    <p>Browse and explore all software quality indicators with detailed information about each one.</p>
                    <a href="./indicators/" class="endpoint-link">Explore Indicators</a>
                </div>
                
                <div class="endpoint-card">
                    <h3>🔧 Tools</h3>
                    <p>Discover tools and frameworks for implementing software quality practices.</p>
                    <a href="./tools/" class="endpoint-link">Explore Tools</a>
                </div>
                
                <div class="endpoint-card">
                    <h3>📐 Dimensions</h3>
                    <p>Understand the various dimensions of software quality assessment.</p>
                    <a href="./dimensions/" class="endpoint-link">Explore Dimensions</a>
                </div>
                
                <div class="endpoint-card">
                    <h3>🔗 Relationships</h3>
                    <p>View relationships between indicators, tools, and dimensions.</p>
                    <a href="./relationships/graph.html" class="endpoint-link">Open Graph Viewer</a>
                </div>
                
                <div class="endpoint-card">
                    <h3>🏥 Health</h3>
                    <p>Check the current health status and metrics of the API.</p>
                    <a href="./health.json" class="endpoint-link">View Health</a>
                </div>
                
                <div class="endpoint-card">
                    <h3>📚 OpenAPI</h3>
                    <p>Full API specification in OpenAPI 3.0 format for integration and documentation.</p>
                    <a href="./openapi.json" class="endpoint-link">View Spec</a>
                </div>
            </div>
        </section>
        
        <section id="features">
            <div class="features">
                <h2>⭐ API Features</h2>
                <ul>
                    <li>RESTful JSON API</li>
                    <li>Pagination support</li>
                    <li>HATEOAS links for navigation</li>
                    <li>JSON-LD structured data</li>
                    <li>OpenAPI 3.0 specification</li>
                    <li>Comprehensive relationship graphs</li>
                    <li>Real-time health monitoring</li>
                    <li>Automatic updates every 6 hours</li>
                    <li>GitHub Pages deployment</li>
                    <li>Zero-cost infrastructure</li>
                </ul>
            </div>
        </section>
        
        <section id="quickstart">
            <div class="quick-start">
                <h2>🚀 Quick Start</h2>
                <p>Get started with the API in seconds:</p>
                
                <h3 style="margin-top: 20px;">Get All Indicators:</h3>
                <div class="code-block">
curl https://vuillaut.github.io/evapi/indicators/ | jq
                </div>
                
                <h3 style="margin-top: 20px;">Get All Tools:</h3>
                <div class="code-block">
curl https://vuillaut.github.io/evapi/tools/ | jq
                </div>
                
                <h3 style="margin-top: 20px;">Get All Dimensions:</h3>
                <div class="code-block">
curl https://vuillaut.github.io/evapi/dimensions/ | jq
                </div>
                
                <h3 style="margin-top: 20px;">Check API Health:</h3>
                <div class="code-block">
curl https://vuillaut.github.io/evapi/health.json | jq
                </div>
            </div>
        </section>
        
        <section id="api">
            <div class="section-title">📡 Using the API</div>
            <p>
                The API is organized into logical collections:
            </p>
            <ul style="margin: 20px 0; padding-left: 20px;">
                <li><strong>Indicators</strong> - Quality metrics and assessment criteria</li>
                <li><strong>Tools</strong> - Software and services for quality assurance</li>
                <li><strong>Dimensions</strong> - Categories of software quality (e.g., reliability, maintainability)</li>
                <li><strong>Relationships</strong> - Connections between all entities</li>
            </ul>
            
            <p style="margin-top: 20px;">
                All endpoints return paginated JSON responses with:
            </p>
            <ul style="margin: 20px 0; padding-left: 20px;">
                <li>Items data</li>
                <li>HATEOAS links for pagination and navigation</li>
                <li>JSON-LD context for semantic understanding</li>
                <li>Metadata about the collection</li>
            </ul>
        </section>
    </div>
    
    <footer>
        <p>
            <strong>EVERSE Unified API</strong> | 
            <a href="https://github.com/vuillaut/evapi">GitHub Repository</a> | 
            <a href="./openapi.json">OpenAPI Specification</a> | 
            <a href="./dashboard.html">Status Dashboard</a> | 
            <a href="./relationships/graph.html">Graph Viewer</a>
        </p>
        <p style="margin-top: 10px; font-size: 0.9em;">
            Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC
        </p>
    </footer>
</body>
</html>"""

    # Write landing page
    landing_file = API_DIR / "index.html"
    with open(landing_file, "w", encoding="utf-8") as f:
        f.write(landing_html)

    print(f"✓ Generated landing page: {landing_file}")


if __name__ == "__main__":
    print("Generating health check and status endpoints...")
    generate_health_endpoint()
    generate_status_endpoint()
    generate_dashboard()
    generate_landing_page()
    print("✓ Health check endpoints generated successfully!")
