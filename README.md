
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

## Known Issues and Future Improvements

### Model Duplication
Currently, the project has some code duplication due to having to define similar models in multiple places:
1. Pydantic models in `models.py` for REST API and data validation
2. Strawberry GraphQL types in `api/graphql_types.py` for GraphQL schema
3. Similar conversion logic between these models

#### Proposed Solution
We can leverage [Strawberry's built-in Pydantic integration](https://strawberry.rocks/docs/integrations/pydantic) to reduce this duplication. Here's how:

1. Install the Strawberry Pydantic extension:
```bash
pip install 'strawberry-graphql[pydantic]'
```

2. Convert Pydantic models to Strawberry types automatically:
```python
from typing import Optional
import strawberry
from strawberry.tools import merge_types
from pydantic import BaseModel, EmailStr

# Define Pydantic model once
class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True

# Automatically convert to Strawberry type
@strawberry.experimental.pydantic.type(UserBase)
class User:
    # Add GraphQL-specific fields or methods
    @strawberry.field
    async def friends(self) -> List["User"]:
        # GraphQL resolver implementation
        pass

# You can also convert input types
@strawberry.experimental.pydantic.input(UserBase)
class UserInput:
    pass
```

This approach provides several benefits:
- Single source of truth for data models
- Automatic validation through [Pydantic's type system](https://docs.pydantic.dev/latest/concepts/types/)
- Type safety across the entire application
- Reduced maintenance overhead
- Consistent data structures

### Implementation Plan

1. Move all base models to `models.py` as [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/)
2. Use [Strawberry's Pydantic integration](https://strawberry.rocks/docs/integrations/pydantic) to convert models for GraphQL
3. Add GraphQL-specific fields using [Strawberry field decorators](https://strawberry.rocks/docs/types/fields)
4. Update resolvers to use the converted types
5. Remove duplicate type definitions

Example refactoring for the User model:

```python
# models.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    referred_by: Optional[str] = None
    referral_code: str

# api/graphql_types.py
import strawberry
from strawberry.tools import merge_types
from models import UserBase

@strawberry.experimental.pydantic.type(UserBase)
class User:
    @strawberry.field
    async def friends(self) -> "UserConnection":
        # GraphQL-specific implementation
        pass

    @strawberry.field
    async def referrer(self) -> Optional["User"]:
        # GraphQL-specific implementation
        pass
```

### Additional Considerations

1. **Performance**: The automatic conversion adds minimal overhead ([Pydantic v2 performance](https://docs.pydantic.dev/latest/concepts/performance/))
2. **Type Safety**: Maintains type checking across REST and GraphQL APIs
3. **Validation**: [Pydantic validation rules](https://docs.pydantic.dev/latest/concepts/validators/) are preserved
4. **Flexibility**: Still allows for API-specific customizations through [Strawberry's extensions](https://strawberry.rocks/docs/guides/extensions)
5. **Maintenance**: Single location for model changes

### Useful Documentation Links

- [Strawberry GraphQL Documentation](https://strawberry.rocks/docs)
  - [Pydantic Integration Guide](https://strawberry.rocks/docs/integrations/pydantic)
  - [Field Customization](https://strawberry.rocks/docs/types/fields)
  - [Type System](https://strawberry.rocks/docs/types/types)

- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
  - [Models Overview](https://docs.pydantic.dev/latest/concepts/models/)
  - [Type System](https://docs.pydantic.dev/latest/concepts/types/)
  - [Validators](https://docs.pydantic.dev/latest/concepts/validators/)
  - [Performance Considerations](https://docs.pydantic.dev/latest/concepts/performance/)

## License

[Add your license information here]
