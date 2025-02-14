
# Simple Model API

A modern FastAPI-based application demonstrating a user management system with GraphQL support, MongoDB integration, and comprehensive testing.

## Features

- RESTful API endpoints for user management
- GraphQL API with Strawberry GraphQL
- Asynchronous MongoDB integration
- Cursor-based pagination
- Referral system
- Friendship management
- Comprehensive test suite
- Database seeding utilities

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) (>= 0.68.0) - Modern, fast web framework for building APIs
- [Strawberry GraphQL](https://strawberry.rocks/) (>= 0.138.0) - GraphQL library leveraging Python type hints
- [Motor](https://motor.readthedocs.io/) (>= 3.3.0) - Async Python driver for MongoDB
- [Pydantic](https://docs.pydantic.dev/) (>= 2.0.0) - Data validation using Python type annotations
- [Uvicorn](https://www.uvicorn.org/) (>= 0.15.0) - Lightning-fast ASGI server
- [pytest](https://docs.pytest.org/) (>= 7.0.0) - Testing framework
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) (>= 0.21.0) - Async support for pytest

## Prerequisites

- Python 3.7+
- MongoDB running locally on port 27017
- pip for package installation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd simple_model
```

2. Install dependencies:
```bash
pip install -e .
```

## Database Setup

Ensure MongoDB is running locally on port 27017. The application will automatically:
- Create required indexes for `uuid`, `email`, and `referral_code` fields
- Set up test database configurations for testing environment

## Running the Application

Start the server:
```bash
python main.py
```

The server will start at `http://0.0.0.0:8001` with auto-reload enabled.

### Available Endpoints

- REST API Documentation: `http://localhost:8001/docs`
- Alternative API Documentation (RapiDoc): `http://localhost:8001/rapidoc`
- GraphQL Playground: `http://localhost:8001/graphql`

## Testing

Run the test suite:
```bash
pytest
```

For verbose output:
```bash
pytest -v
```

## Database Seeding

To populate the database with sample data:
```bash
python scripts/seed_database.py
```

This will create:
- 10 random users
- 8 friendships
- 4 referrals

## API Features

### REST Endpoints

- User Management (CRUD operations)
- Friendship Management
- Referral System
- Pagination Support
- Active Users Filtering

### GraphQL Features

- User Queries and Mutations
- Friendship Management
- Referral Statistics
- Cursor-based Pagination
- Advanced Filtering

## Project Structure

```
simple_model/
├── api/
│   ├── graphql_schema.py    # GraphQL schema definitions
│   ├── graphql_types.py     # GraphQL type definitions
│   └── user_router.py       # REST API routes
├── services/
│   └── user_service.py      # Business logic
├── tests/
│   └── conftest.py          # Test configurations
├── utils/
│   └── pagination.py        # Pagination utilities
├── database.py              # Database connection management
├── main.py                  # Application entry point
├── models.py               # Pydantic models
└── scripts/
    └── seed_database.py     # Database seeding utility
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

[Add your license information here]
