# Backend Tests

This directory contains tests for the CrossPostMe backend.

## Running Tests

### Run all tests

```bash
pytest
```

### Run specific test file

```bash
pytest tests/test_db_connection.py -v
```

### Run tests with specific markers

```bash
# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit
```

### Run as Python module (no pytest required)

```bash
python -m tests.test_db_connection
```

## Test Structure

- `tests/test_db_connection.py` - Database connection and operations tests
- `tests/conftest.py` - Pytest configuration and fixtures
- `pytest.ini` - Pytest settings

## Adding New Tests

1. Create new test files with `test_` prefix
2. Use proper imports: `from db import get_db`
3. Mark tests appropriately:
   - `@pytest.mark.integration` for tests needing external services
   - `@pytest.mark.unit` for isolated unit tests
   - `@pytest.mark.slow` for long-running tests

## Environment

Tests use the same `.env` configuration as the main application.
Ensure `MONGO_URL` and `DB_NAME` are set correctly.

## Continuous Integration

For CI/CD, install the backend package in editable mode:

```bash
pip install -e .
```

Or set PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```
