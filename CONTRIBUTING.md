# Contributing to EVERSE Unified API

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and supportive of other contributors.

## How to Contribute

### Reporting Issues

1. Check if issue already exists
2. Include detailed description
3. Provide steps to reproduce
4. Add relevant code examples
5. Mention your environment

**Template:**
```markdown
## Description
Brief description of the issue

## Steps to Reproduce
1. ...
2. ...

## Expected Behavior
What should happen?

## Actual Behavior
What actually happened?

## Environment
- OS: [e.g., macOS 12.0]
- Python: [e.g., 3.11]
- etc.
```

### Suggesting Enhancements

1. Use clear, descriptive title
2. Provide detailed description
3. Explain use case
4. List any alternatives considered

### Pull Request Process

1. **Fork the repository**
```bash
gh repo fork EVERSE-ResearchSoftware/unified-api
```

2. **Create feature branch**
```bash
git checkout -b feature/amazing-feature
```

3. **Make your changes**
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation

4. **Test your changes**
```bash
pytest tests/ --cov=scripts
pre-commit run --all-files
```

5. **Commit your changes**
```bash
git commit -m "feat(module): description of change"
```

6. **Push to your fork**
```bash
git push origin feature/amazing-feature
```

7. **Open Pull Request**
   - Provide clear description
   - Reference related issues
   - Include screenshots if applicable

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- pip

### Installation

```bash
git clone https://github.com/YOUR-USERNAME/unified-api.git
cd unified-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Pre-commit Hooks

```bash
pre-commit install
```

## Making Changes

### Code Style

Follow PEP 8 with these tools:

- **Black**: Code formatting
```bash
black scripts/ tests/
```

- **Flake8**: Linting
```bash
flake8 scripts/ tests/
```

- **isort**: Import sorting
```bash
isort scripts/ tests/
```

- **mypy**: Type checking
```bash
mypy scripts/
```

### Testing

Write tests for all new functionality:

```python
# tests/test_my_feature.py
import pytest
from scripts.my_module import my_function

class TestMyFeature:
    def test_my_function_basic(self):
        result = my_function("input")
        assert result == "expected"

    def test_my_function_error(self):
        with pytest.raises(ValueError):
            my_function(None)
```

Run tests before committing:

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_my_feature.py

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html

# Check coverage
open htmlcov/index.html
```

### Documentation

Update documentation for:
- New features
- API changes
- Configuration options
- Examples

Use docstrings in Google format:

```python
def my_function(param1: str, param2: int = 5) -> bool:
    """
    Short description (one line).

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 5)

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
    """
```

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/changes
- `chore`: Build, dependencies, etc.

### Subject
- Imperative mood ("add" not "adds")
- No period at the end
- Max 50 characters

### Body
- Explain what and why
- Wrap at 72 characters
- References to issues

### Example
```
feat(fetch_indicators): add retry logic for GitHub API

- Implement exponential backoff for failed requests
- Add max retries configuration
- Include logging for retry attempts

Fixes #42
```

## Asking for Help

- **Questions**: Start a discussion
- **Issues**: Open an issue
- **Chat**: Join EVERSE Slack channel
- **Email**: contact@everse.software

## Review Process

Maintainers will review PRs within 5 business days:

1. Check for compliance with guidelines
2. Review code quality
3. Run automated tests
4. Provide feedback or approve

Address review comments by:
1. Making requested changes
2. Pushing to your branch
3. Responding to comments
4. Requesting re-review

## Merge Criteria

PRs can be merged when:
- ✅ All tests pass
- ✅ Code review approved
- ✅ Documentation updated
- ✅ No conflicts with main branch

## After Merge

- Your changes will be included in the next release
- You'll be credited as a contributor
- Monitor for any issues related to your changes

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes
- CONTRIBUTORS.md file

## Questions?

- Check existing issues and discussions
- Review documentation
- Ask maintainers

Thank you for contributing! 🎉
