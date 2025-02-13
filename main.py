from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.responses import HTMLResponse
from database import Database
from api.user_router import router as user_router
import uvicorn
from models import RootResponse
from strawberry.fastapi import GraphQLRouter
from api.graphql_schema import schema

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await Database.connect_db()
    yield
    # Shutdown
    await Database.close_db()

app = FastAPI(
    title="Simple CRUD API",
    lifespan=lifespan
)

# Create GraphQL router with GraphiQL playground enabled
graphql_router = GraphQLRouter(
    schema,
    graphiql=True  # This enables the GraphiQL interface
)

# Add GraphQL routes to the app (make sure this is before other routes)
app.include_router(graphql_router, prefix="/graphql")


@app.get("/rapidoc", include_in_schema=False)
async def rapidoc():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple CRUD API - RapiDoc</title>
        <meta charset="utf-8">
        <script type="module" src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"></script>
    </head>
    <body>
        <rapi-doc 
            spec-url="/openapi.json"
            theme="dark"
            show-header="false"
            render-style="read"
            primary-color="#2d87e2"
        > </rapi-doc>
    </body>
    </html>
    """)

@app.get("/", response_model=RootResponse)
async def root() -> RootResponse:
    return RootResponse(
        message="Welcome to the Users API",
        docs="/docs",
        endpoints={
            "graphql_playground": "/graphql",  # Add this to show GraphQL endpoint
            "create_user": "POST /users/",
            "get_all_users": "GET /users/?page=1&page_size=10",
            "get_user": "GET /users/{uuid}",
            "get_user_by_email": "GET /users/email/{email}",
            "get_users_count": "GET /users/count",
            "get_active_users": "GET /users/active",
            "update_user": "PUT /users/{uuid}",
            "patch_user": "PATCH /users/{uuid}",
            "delete_user": "DELETE /users/{uuid}"
        }
    )

app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
