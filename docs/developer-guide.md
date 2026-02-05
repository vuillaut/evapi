# Developer Guide

## Getting Started

### Environment Setup

```bash
# Clone repository
git clone https://github.com/EVERSE-ResearchSoftware/unified-api.git
cd unified-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development tools
pip install -r requirements-dev.txt
```

### Pre-commit Setup

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Project Architecture

### Data Flow

```
GitHub Repositories
    ↓
Fetch Scripts (fetch_*.py)
    ↓
Data Models (models.py)
    ↓
Relationship Builder (build_relationships.py)
    ↓
Validation (validate.py)
    ↓
API Generator (generate_api.py)
    ↓
JSON Files (api/v1/)
    ↓
GitHub Pages Deployment
```

### Key Components

#### Configuration (`scripts/config.py`)
Centralized configuration for:
- GitHub repository locations
- API URLs and contexts
- Timeout and retry settings
- File paths

#### Utilities (`scripts/utils.py`)
Common functions:
- HTTP request handling with retries
- GitHub API interaction
- JSON file I/O
- Session management with authentication

#### Data Models (`scripts/models.py`)
Pydantic models for:
- Indicator
- Tool
- Dimension
- Task
- Pipeline
- RelationshipEdge
- APIResponse

#### Data Fetchers
Individual fetchers for each data source:
- `fetch_indicators.py` - EVERSE indicators
- `fetch_tools.py` - TechRadar tools
- `fetch_dimensions.py` - Quality dimensions

Each fetcher:
1. Fetches raw data from GitHub
2. Validates against data models
3. Caches results locally
4. Provides error handling

#### Relationship Builder (`scripts/build_relationships.py`)
Builds bidirectional relationships:
- Tool → Indicator (measures)
- Indicator → Tool (measured_by)
- Dimension → Indicator (contains)
- Indicator → Dimension (part_of)

Provides query methods:
- `get_tools_for_indicator(id)`
- `get_indicators_for_tool(id)`
- `get_indicators_for_dimension(id)`

#### API Generator (`scripts/generate_api.py`)
Main orchestration script:
1. Fetches all data
2. Validates collections
3. Builds relationships
4. Generates API files
5. Validates output

## Development Workflow

### Adding a New Data Source

1. **Create fetcher** (`scripts/fetch_newsource.py`):
```python
from models import MyModel
from utils import fetch_json, list_github_files

def fetch_and_validate_mydata(use_cache=True):
    # Load from cache if exists
    # Fetch from GitHub
    # Validate and return
    pass
```

2. **Create data model** (in `scripts/models.py`):
```python
class MyModel(BaseModel):
    id: str
    name: str
    # ... other fields
```

3. **Add to generator** (in `scripts/generate_api.py`):
```python
def generate_mydata_collection(items):
    # Generate endpoint files
    pass

# In main():
mydata = fetch_and_validate_mydata()
generate_mydata_collection(mydata)
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=scripts --cov-report=html

# Run specific test
pytest tests/test_models.py::TestIndicator::test_indicator_creation

# Run with verbose output
pytest tests/ -v

# Run and watch for changes
ptw tests/
```

### Debugging

```bash
# Enable verbose logging
cd scripts
python generate_api.py --verbose

# Use Python debugger
python -m pdb generate_api.py

# Check cached data
ls -la .cache/
cat .cache/indicators.json | jq .
```

## Code Standards

### Style Guide

The project uses:
- **Black** for formatting (line length: 88)
- **Flake8** for linting
- **isort** for import organization
- **mypy** for type checking

### Pre-commit Checks

Configured hooks enforce:
- Code formatting
- Linting
- Import sorting
- Trailing whitespace
- Large file detection

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `CONSTANT_CASE`
- **Private members**: `_private_member`

### Documentation

- Docstrings in Google format
- Type hints on all functions
- Comments for complex logic
- README sections for modules

### Example Code

```python
"""Module description."""

from typing import List, Dict, Optional

from models import MyModel


def process_items(
    items: List[MyModel],
    filter_by: Optional[str] = None,
) -> Dict[str, MyModel]:
    """
    Process a list of items.

    Args:
        items: List of items to process
        filter_by: Optional filter criterion

    Returns:
        Dictionary of processed items
    """
    result = {}

    for item in items:
        if filter_by and item.category != filter_by:
            continue

        result[item.id] = item

    return result
```

## Git Workflow

### Branch Naming
- Feature: `feature/short-description`
- Bug: `fix/short-description`
- Hotfix: `hotfix/short-description`

### Commit Messages
```
type(scope): short description (< 50 chars)

Longer explanation if needed (wrapped at 72 chars).

Refs #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

### Pull Request Process

1. Create feature branch from `main`
2. Make changes and commit
3. Push to your fork
4. Create PR with description
5. Address review comments
6. Merge when approved

## Troubleshooting

### Import Errors

```python
# Ensure you're in the scripts directory or add to path
import sys
sys.path.insert(0, '/path/to/unified-api/scripts')
```

### GitHub API Rate Limiting

Use GitHub token:
```bash
export GITHUB_TOKEN=your_token_here
python generate_api.py
```

### Failed Data Fetching

1. Check GitHub token
2. Verify repository URLs
3. Check network connectivity
4. Review error logs

```bash
python generate_api.py --verbose 2>&1 | grep -i error
```

### Validation Failures

```bash
# Check what failed
cat .cache/relationships.json | jq '.edges | length'

# Review individual items
cat .cache/indicators.json | jq '.items[] | select(.id == "license")'
```

## Performance Considerations

### Caching Strategy

- Data cached in `.cache/` directory
- Reused if available
- Can be skipped with `--skip-cache`
- Cleared by removing `.cache/` directory

### Optimization Tips

1. Use cache during development
2. Test with small data sets
3. Profile with `cProfile`:
```python
import cProfile
cProfile.run('generate_api.py')
```

4. Monitor memory usage:
```bash
python -m memory_profiler generate_api.py
```

## Resources

- **Pydantic**: https://docs.pydantic.dev/
- **Requests**: https://requests.readthedocs.io/
- **JSON-LD**: https://www.w3.org/TR/json-ld11/
- **GitHub API**: https://docs.github.com/en/rest

## Getting Help

- Check existing issues: https://github.com/EVERSE-ResearchSoftware/unified-api/issues
- Review documentation: `docs/` directory
- Contact maintainers: [contact info]
