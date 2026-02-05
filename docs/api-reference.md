# API Reference

## Overview

The EVERSE Unified API provides RESTful access to quality indicators, tools, and their relationships.

**Base URL:** `https://everse.software/api/v1/`

**Content Type:** `application/json` or `application/ld+json`

## Endpoints

### Root Endpoint

**GET** `/`

Returns the API root with links to all available endpoints.

**Response:**
```json
{
  "@context": "https://w3id.org/everse/api/v1/context.jsonld",
  "@type": "APIRoot",
  "version": "v1",
  "endpoints": {
    "indicators": "https://everse.software/api/v1/indicators/",
    "tools": "https://everse.software/api/v1/tools/",
    "dimensions": "https://everse.software/api/v1/dimensions/",
    "relationships": "https://everse.software/api/v1/relationships/"
  }
}
```

### Indicators Collection

**GET** `/indicators/`

List all quality indicators.

**Query Parameters:**
- `dimension` (string) - Filter by dimension ID
- `category` (string) - Filter by category

**Response:**
```json
{
  "@context": "https://w3id.org/everse/api/v1/context.jsonld",
  "@type": "Collection",
  "name": "Indicators",
  "totalItems": 42,
  "items": [
    {
      "id": "license",
      "name": "License",
      "description": "Software has a clear license"
    }
  ]
}
```

### Single Indicator

**GET** `/indicators/{id}`

Get detailed information about a specific indicator.

**Response:**
```json
{
  "@context": "https://w3id.org/everse/api/v1/context.jsonld",
  "@type": "Indicator",
  "id": "license",
  "name": "License",
  "description": "Software has a clear and permissive license",
  "dimension": "legal",
  "related_tools": ["howfairis", "reuse"]
}
```

### Tools Collection

**GET** `/tools/`

List all quality assessment tools.

**Query Parameters:**
- `ring` (string) - Filter by ring: adopt, trial, assess, hold
- `quadrant` (string) - Filter by quadrant

**Response:**
```json
{
  "@context": "https://w3id.org/everse/api/v1/context.jsonld",
  "@type": "Collection",
  "name": "Tools",
  "totalItems": 28,
  "items": [
    {
      "id": "howfairis",
      "name": "How FAIR is it",
      "ring": "adopt"
    }
  ]
}
```

### Single Tool

**GET** `/tools/{id}`

Get detailed information about a specific tool.

**Response:**
```json
{
  "@context": "https://w3id.org/everse/api/v1/context.jsonld",
  "@type": "Tool",
  "id": "howfairis",
  "name": "How FAIR is it",
  "description": "A web-based tool to assess FAIRness of research software",
  "url": "https://fairsoftware.nl",
  "ring": "adopt",
  "related_indicators": ["license", "documentation", "testing"]
}
```

### Tools by Indicator

**GET** `/tools/by-indicator/{indicator_id}`

Get all tools that measure a specific indicator.

**Response:**
```json
{
  "@context": "https://w3id.org/everse/api/v1/context.jsonld",
  "@type": "Collection",
  "name": "Tools for License Indicator",
  "totalItems": 3,
  "items": [
    {"id": "howfairis", "name": "How FAIR is it"},
    {"id": "reuse", "name": "REUSE Tool"}
  ]
}
```

### Dimensions Collection

**GET** `/dimensions/`

List all quality dimensions.

**Response:**
```json
{
  "@context": "https://w3id.org/everse/api/v1/context.jsonld",
  "@type": "Collection",
  "name": "Dimensions",
  "totalItems": 8,
  "items": [
    {
      "id": "legal",
      "name": "Legal",
      "description": "Legal aspects of software quality"
    }
  ]
}
```

### Single Dimension

**GET** `/dimensions/{id}`

Get detailed information about a specific dimension.

**Response:**
```json
{
  "@context": "https://w3id.org/everse/api/v1/context.jsonld",
  "@type": "Dimension",
  "id": "legal",
  "name": "Legal",
  "description": "Legal aspects of software quality",
  "indicators": ["license", "copyright"]
}
```

### Relationship Graph

**GET** `/relationships/graph`

Get the complete knowledge graph of all relationships.

**Query Parameters:**
- `format` (string) - Output format: json (default), graphviz, cypher
- `depth` (integer) - Relationship depth (default: 2)

**Response:**
```json
{
  "@context": "https://w3id.org/everse/api/v1/context.jsonld",
  "@type": "Graph",
  "statistics": {
    "total_indicators": 42,
    "total_tools": 28,
    "total_dimensions": 8,
    "total_relationships": 156
  },
  "edges": [
    {
      "source_id": "howfairis",
      "source_type": "Tool",
      "target_id": "license",
      "target_type": "Indicator",
      "relationship_type": "measures"
    }
  ]
}
```

## Response Format

All successful responses return HTTP 200 with JSON data. All responses include:

- `@context` - JSON-LD context for semantic meaning
- `@type` - Entity type
- `generated` - ISO 8601 timestamp of generation

## Error Handling

**400 Bad Request**
```json
{
  "@context": "...",
  "@type": "Error",
  "error": "invalid_parameter",
  "message": "Invalid parameter: ring",
  "timestamp": "2026-02-05T14:30:00Z"
}
```

**404 Not Found**
```json
{
  "@context": "...",
  "@type": "Error",
  "error": "not_found",
  "message": "Indicator 'unknown' not found",
  "timestamp": "2026-02-05T14:30:00Z"
}
```

**500 Internal Server Error**
```json
{
  "@context": "...",
  "@type": "Error",
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "timestamp": "2026-02-05T14:30:00Z"
}
```

## Rate Limiting

Currently, no rate limiting is enforced. However, please be respectful of the service.

## CORS

All endpoints support CORS requests with the following headers:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Accept`

## JSON-LD Contexts

The API uses JSON-LD contexts for semantic meaning. Contexts define the vocabulary used:

- API Context: `https://w3id.org/everse/api/v1/context.jsonld`

## Updates

The API is regenerated automatically every 6 hours. The exact update time is available in the HTTP headers:

- `X-Generated-At` - ISO 8601 timestamp of last generation
- `X-Data-Version` - Version identifier of the data

## Examples

### Get all FAIR-related indicators

```bash
curl "https://everse.software/api/v1/indicators/?category=FAIR" \
  -H "Accept: application/json"
```

### Find tools measuring code quality

```bash
curl "https://everse.software/api/v1/tools/by-indicator/code-quality" \
  -H "Accept: application/json" | jq '.items[] | {id, name}'
```

### Export relationship graph as GraphViz

```bash
curl "https://everse.software/api/v1/relationships/graph?format=graphviz" \
  > graph.gv
dot -Tpng graph.gv -o graph.png
```
