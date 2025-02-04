from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from starlette.responses import HTMLResponse
from models import User, UserCreate, UserBase
from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel
import uvicorn
import strawberry
from strawberry.fastapi import GraphQLRouter

app = FastAPI(
    title="Simple CRUD API",
    docs_url=None,  # Disable default Swagger UI
    redoc_url=None  # Disable default ReDoc
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

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

# In-memory storage for this example
users_db = {}
counter = 1

class RootResponse(BaseModel):
    message: str
    docs: str
    endpoints: Dict[str, str]

@app.get("/", response_model=RootResponse)
async def root() -> RootResponse:
    return RootResponse(
        message="Welcome to the Users API",
        docs="/docs",
        endpoints={
            "create_user": "POST /users/",
            "get_all_users": "GET /users/",
            "get_user": "GET /users/{user_id}",
            "update_user": "PUT /users/{user_id}",
            "delete_user": "DELETE /users/{user_id}"
        }
    )

@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    global counter
    user_dict = user.model_dump()
    del user_dict["password"]  # In a real app, you'd hash the password
    
    new_user = User(
        id=counter,
        created_at=datetime.now(),
        **user_dict
    )
    users_db[counter] = new_user
    counter += 1
    return new_user

@app.get("/users/", response_model=List[User])
async def read_users():
    return list(users_db.values())

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserBase):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_dict = user.model_dump()
    updated_user = User(
        id=user_id,
        created_at=users_db[user_id].created_at,
        **user_dict
    )
    users_db[user_id] = updated_user
    return updated_user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    return {"message": "User deleted successfully"}

@strawberry.type
class User:
    id: int
    name: str
    email: str

@strawberry.type
class Query:
    @strawberry.field
    async def users(self) -> list[User]:
        return [User(**user.dict()) for user in users_db.values()]

schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
