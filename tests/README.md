# Testing Guide

## Prerequisites

- Python with pytest installed
- MongoDB running locally on port 27017
- pytest-asyncio package (for async test support)

## Test Database Setup

The tests use a dedicated MongoDB database named `test_user_db`. The test configuration automatically:
- Creates required indexes for `uuid`, `email`, and `referral_code` fields
- Drops the test database after each test
- Closes database connections

## Available Fixtures

### `setup_test_database`
- Automatically used in all tests
- Sets up a fresh test database connection
- Creates required indexes
- Cleans up after each test

### `sample_user`
- Creates a test user with the following data:
  ```python
  {
      "email": "test@example.com",
      "name": "Test User",
      "password": "testpassword123"
  }
  ```

## Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_file.py
```

## Writing Tests

Example of using the `sample_user` fixture:

```python
async def test_user_creation(sample_user):
    assert sample_user["email"] == "test@example.com"
    assert sample_user["name"] == "Test User"
```
