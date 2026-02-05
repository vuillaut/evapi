# EVERSE Unified API

A centralized, open-source API that aggregates and exposes data from multiple EVERSE research software quality services through a standardized RESTful interface.

## Features

- 🔄 **Unified Access** - Single entry point for all EVERSE services
- 🔗 **Bidirectional Linking** - Automatic relationship mapping
- 📊 **Knowledge Graph** - Complete relationship graph for discovery
- ⚡ **Fast Updates** - Data automatically refreshed every 6 hours
- 🆓 **Zero Cost** - Entirely free, hosted on GitHub Pages
- 🛠️ **Easy Maintenance** - Python-based, well-documented

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate API
cd scripts
python generate_api.py
```

## API Endpoints

- `GET /api/v1/` - API root
- `GET /api/v1/indicators/` - List all indicators
- `GET /api/v1/tools/` - List all tools
- `GET /api/v1/dimensions/` - List all dimensions
- `GET /api/v1/relationships/graph` - Full knowledge graph

## Data Sources

- **Indicators** - https://github.com/EVERSE-ResearchSoftware/indicators
- **TechRadar** - https://github.com/EVERSE-ResearchSoftware/TechRadar
- **RSQKit** - https://everse.software/RSQKit/
- **resqui** - https://github.com/EVERSE-ResearchSoftware/QualityPipelines
- **DashVERSE** - https://github.com/EVERSE-ResearchSoftware/DashVERSE

## Testing

```bash
pytest tests/ --cov=scripts
```

## License

Apache 2.0