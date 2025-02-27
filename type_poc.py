from __future__ import annotations  # Required for self-referencing types

import uuid
from datetime import datetime
from typing import Annotated, Optional, ForwardRef, List, TypeVar, Generic, Type, Any, Union

from pydantic import BaseModel, StringConstraints, ConfigDict, Field

UUID4Str = Annotated[str, StringConstraints(
    pattern="^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")]

def readonly(field=None, *, default=...):
    """Decorator to mark fields as readonly"""
    return Field(default=default, json_schema_extra={'readonly': True})



class JelloEntity(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        # strict=True, # Fix the issue with Pydantic and FastAPI for Enum and UUID fields before enabling this
        use_enum_values=True,
    )

    uuid: UUID4Str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        json_schema_extra={
            'readonly': True,
            "audit": True
        }
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        json_schema_extra={
            'readonly': True,
            "audit": True
        }
    )
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None



def Association(
    entityType: Type[JelloEntity],
    mappedBy: str,
    filteredBy: Optional[str] = None,
    **kwargs: Any
) -> Any:
    json_schema_extra = {
        'association': {
            'mappedBy': mappedBy,
            'entityType': entityType.__forward_arg__ if isinstance(entityType, ForwardRef) else entityType.__name__,
        }
    }

    if filteredBy:
        json_schema_extra['association']['filteredBy'] = filteredBy

    if 'json_schema_extra' in kwargs:
        existing_extra = kwargs.pop('json_schema_extra')
        json_schema_extra.update(existing_extra)

    return Field(**kwargs, json_schema_extra=json_schema_extra)


def Ref(entityType: Type[JelloEntity], **kwargs: Any) -> Any:
    json_schema_extra = {
        'ref': {
            'entityType': entityType.__name__,
        }
    }

    # Merge any existing json_schema_extra from kwargs
    if 'json_schema_extra' in kwargs:
        existing_extra = kwargs.pop('json_schema_extra')
        json_schema_extra.update(existing_extra)

    return Field(UUID4Str, **kwargs, json_schema_extra=json_schema_extra)


class Category(JelloEntity):
    name: str
    description: Optional[str] = None
    parent: Optional[Ref(Category)] = None  # ???
    p3: Ref(Product, required=True)
    p2: Ref(Product)
    products: Association(Product, mappedBy='category_ref')
    cheapestInCategory: Association(Product, mappedBy='category', filteredBy="price<99")


class Product(JelloEntity):
    name: str
    description: Optional[str] = None
    price: float
    category_embedded: Category
    category_ref: Ref(Category)
    
if __name__ == '__main__':
    n = int(input("Enter a number: s"))
    for i in range(1,n+1):
        print(i,end="")