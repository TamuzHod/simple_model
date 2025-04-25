
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
- Environment-based configuration

## Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) (>= 0.68.0) - Modern, fast web framework for building APIs
- [Strawberry GraphQL](https://strawberry.rocks/) (>= 0.138.0) - GraphQL library leveraging Python type hints
- [Motor](https://motor.readthedocs.io/) (>= 3.3.0) - Async Python driver for MongoDB
- [Pydantic](https://docs.pydantic.dev/) (>= 2.0.0) - Data validation using Python type annotations
- [Uvicorn](https://www.uvicorn.org/) (>= 0.15.0) - Lightning-fast ASGI server
- [pytest](https://docs.pytest.org/) (>= 7.0.0) - Testing framework
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) (>= 0.21.0) - Async support for pytest
- [python-dotenv](https://pypi.org/project/python-dotenv/) (>= 1.0.0) - Environment variable management

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

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env_sample .env
# Edit .env with your MongoDB credentials if needed
```

## Environment Configuration

The application uses environment variables for configuration. Create a `.env` file based on `.env_sample`:

```env
MONGODB_USER=
MONGODB_PASSWORD=
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_TLS=false
```

For local development without authentication, you can leave `MONGODB_USER` and `MONGODB_PASSWORD` empty.

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
- 5 sample users
- 3 friendships
- 1 referred user

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
│   ├── conftest.py          # Test configurations
│   ├── test_user_service.py # Service tests
│   └── integration/         # Integration tests
├── utils/
│   └── pagination.py        # Pagination utilities
├── scripts/
│   └── seed_database.py     # Database seeding utility
├── database.py              # Database connection management
├── main.py                  # Application entry point
├── models.py               # Pydantic models
├── requirements.txt        # Project dependencies
├── .env_sample            # Environment variables template
└── README.md              # This file
```

## API Examples

### REST API

Create a user:
```bash
curl -X POST http://localhost:8001/users/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "name": "John Doe", "password": "password123"}'
```

Get all users:
```bash
curl http://localhost:8001/users/
```

### GraphQL API

Query users:
```graphql
query {
  users(first: 10) {
    edges {
      node {
        uuid
        name
        email
        referralCode
      }
    }
  }
}
```

Create a user:
```graphql
mutation {
  createUser(
    email: "user@example.com"
    name: "John Doe"
    password: "password123"
  ) {
    uuid
    name
    email
  }
}
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

### Testing Improvements
Currently, our test suite covers basic functionality, but we can enhance it with more comprehensive testing approaches:

1. Test organization is basic
2. Mocking could be more extensive
3. Test data management could be improved
4. GraphQL testing coverage could be expanded
5. Performance testing is missing

#### Proposed Solution
We can implement a more robust testing strategy using pytest's advanced features and best practices:

1. Install additional testing dependencies:
```bash
pip install pytest-cov pytest-asyncio pytest-mock pytest-xdist
```

2. Implement structured test organization:
```python
tests/
├── unit/
│   ├── test_models.py       # Test Pydantic models
│   ├── test_services.py     # Test business logic
│   └── test_utils.py        # Test utilities
├── integration/
│   ├── test_api.py         # Test REST endpoints
│   ├── test_graphql.py     # Test GraphQL resolvers
│   └── test_database.py    # Test MongoDB operations
├── performance/
│   └── test_load.py        # Load testing
└── conftest.py             # Shared fixtures
```

3. Enhanced fixture system:
```python
# conftest.py
import pytest
from typing import AsyncGenerator, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from models import UserBase

@pytest.fixture(scope="session")
async def mongo_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    yield client
    await client.close()

@pytest.fixture(scope="function")
async def test_db(mongo_client: AsyncIOMotorClient) -> AsyncGenerator[AsyncIOMotorClient, None]:
    db = mongo_client.test_db
    yield db
    await db.drop_collection("users")
    await db.drop_collection("friendships")

@pytest.fixture
async def sample_users(test_db) -> Dict[str, UserBase]:
    users = {
        "alice": UserBase(
            email="alice@example.com",
            name="Alice Test",
            is_active=True
        ),
        "bob": UserBase(
            email="bob@example.com",
            name="Bob Test",
            is_active=True
        )
    }
    # Insert users and store their IDs
    for key, user in users.items():
        result = await test_db.users.insert_one(user.model_dump())
        users[key].id = str(result.inserted_id)
    return users
```

4. GraphQL-specific testing utilities:
```python
# tests/integration/test_graphql.py
import strawberry
from typing import Any, Dict
from strawberry.test import GraphQLTestClient

@pytest.fixture
def graphql_client(app) -> GraphQLTestClient:
    return GraphQLTestClient(app)

async def test_user_query(graphql_client: GraphQLTestClient, sample_users: Dict[str, Any]):
    query = """
        query GetUser($email: String!) {
            user(email: $email) {
                email
                name
                isActive
                friends {
                    edges {
                        node {
                            email
                        }
                    }
                }
            }
        }
    """

    variables = {"email": sample_users["alice"].email}
    response = await graphql_client.query(query, variables)

    assert response.errors is None
    assert response.data["user"]["email"] == sample_users["alice"].email
```

5. Performance testing setup:
```python
# tests/performance/test_load.py
import asyncio
import pytest
from httpx import AsyncClient
from typing import List

async def make_requests(client: AsyncClient, n_requests: int) -> List[float]:
    timings = []
    for _ in range(n_requests):
        start = asyncio.get_event_loop().time()
        await client.get("/users/")
        end = asyncio.get_event_loop().time()
        timings.append(end - start)
    return timings

@pytest.mark.performance
async def test_users_endpoint_performance(client: AsyncClient):
    n_requests = 100
    timings = await make_requests(client, n_requests)

    avg_response_time = sum(timings) / len(timings)
    assert avg_response_time < 0.1  # 100ms threshold
```

### Benefits

1. **Improved Organization**:
   - Clear separation between unit, integration, and performance tests
   - Better test discovery and maintenance
   - Easier CI/CD integration

2. **Better Test Data Management**:
   - Centralized fixture management
   - Automatic cleanup between tests
   - Reduced test interference

3. **Comprehensive Coverage**:
   - REST API testing
   - GraphQL query and mutation testing
   - Database operation testing
   - Performance benchmarking

4. **Enhanced Development Experience**:
   - Parallel test execution with pytest-xdist
   - Coverage reporting with pytest-cov
   - Automatic test discovery

### Implementation Plan

1. Restructure test directory
2. Implement shared fixtures
3. Add GraphQL-specific tests
4. Set up performance testing
5. Configure CI/CD integration

### Running Tests

Basic test execution:
```bash
pytest
```

With coverage report:
```bash
pytest --cov=app tests/
```

Parallel execution:
```bash
pytest -n auto
```

Performance tests only:
```bash
pytest tests/performance -m performance
```

### Useful Documentation Links

- [pytest Documentation](https://docs.pytest.org/)
  - [Fixtures](https://docs.pytest.org/en/stable/fixture.html)
  - [Marks](https://docs.pytest.org/en/stable/mark.html)
  - [Parametrizing](https://docs.pytest.org/en/stable/parametrize.html)

- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
  - [Async Tests](https://fastapi.tiangolo.com/advanced/async-tests/)
  - [Dependencies in Tests](https://fastapi.tiangolo.com/advanced/testing-dependencies/)

- [Strawberry Testing](https://strawberry.rocks/docs/guides/testing)
  - [Testing Queries](https://strawberry.rocks/docs/guides/testing#testing-queries)
  - [Testing Mutations](https://strawberry.rocks/docs/guides/testing#testing-mutations)

- [Motor Testing](https://motor.readthedocs.io/en/stable/testing.html)
  - [AsyncIO Integration](https://motor.readthedocs.io/en/stable/testing.html#asyncio-integration)
  - [Test Utilities](https://motor.readthedocs.io/en/stable/testing.html#test-utilities)



### Sample GraphQL Queries

Here are some example queries you can use in the GraphQL Playground:

```graphql
# Get a list of users with basic information
query GetUsers {
  users(first: 20) {
    edges {
      node {
        uuid
        name
        email
        isActive
      }
    }
    totalCount
  }
}

# Get a specific user and their friends
query GetUserWithFriends {
  user(uuid: "67afa2945d9579aa178f23d7") {
    name
    email
    friends {
      edges {
        node {
          name
          email
        }
      }
    }
  }
}

# Get a user with their referral information
query GetUserWithReferrals {
  user(uuid: "67afa2945d9579aa178f23d7") {
    name
    referredUsers {
      edges {
        node {
          name
          email
        }
      }
    }
    referrer {
      name
      email
    }
  }
}

# Get users with pagination information
query UsersWithFriends($pageSize: Int = 15) {
  users(first: $pageSize) {
    edges {
      node {
        uuid
        email
        name
        isActive
        createdAt
        updatedAt
        referredBy
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}

# Get users with both friends and referrals
query UsersWithFriendsAndRefferals($pageSize: Int = 15) {
  users(first: $pageSize) {
    edges {
      node {
        uuid
        email
        name
        isActive
        createdAt
        updatedAt
        referredBy
        referredUsers(first: 10) {
          edges {
            node {
              name
            }
          }
          totalCount
        }
        friends(first: 10) {
          edges {
            node {
              name
            }
          }
          totalCount
        }
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

[Rest of the original content...]


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the excellent web framework
- Strawberry GraphQL for the intuitive GraphQL implementation
- MongoDB for the flexible document database
