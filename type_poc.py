from __future__ import annotations  # Required for self-referencing types

import json
import uuid
from datetime import datetime
from typing import _SpecialForm, Annotated, Optional, ForwardRef, List, TypeVar, Generic, Type, Any, Union
from pydantic._internal._generics import get_args


from pydantic import BaseModel, StringConstraints, ConfigDict, Field

UUID4Str = Annotated[str, StringConstraints(
    pattern="^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")]



@_SpecialForm
def Readonly(self, type):
    """Special form to mark a field as readonly.
    
    Example:
        name: ReadOnlyField[str]
    """
    return Annotated[type, Field(json_schema_extra={'readonly': True})]


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



T = TypeVar('T', bound=JelloEntity)

class Association(BaseModel, Generic[T]):
    def __init__(
        self,
        entityType: Type[T],
        mappedBy: str,
        filteredBy: Optional[str] = None,

    ):
        self.entityType = entityType
        self.mappedBy = mappedBy
        self.filteredBy = filteredBy

    uuids: Optional[List[UUID4Str]] = None
    instances: Optional[List[T]] = None
    def get_instances(self) -> List[T]:
        if self.instances is None:
            self.instances = [{'uuid': uuid, 'name': 'C-123'} for uuid in self.uuids]  # Replace with actual instance retrieval
        return self.instances
    def get_uuids(self) -> List[UUID4Str]:
        if self.uuids is None:
            self.uuids = [instance['uuid'] for instance in self.instances]  # Replace with actual instance retrieval
        return self.uuids
    def count(self) -> int:
        if self.uuids is not None:
            return len(self.uuids)
        return 7  # Replace with actual count retrieval
    

def association(
    mappedBy: str,
    filteredBy: Optional[str] = None,
    **kwargs: Any
) -> Any:
    json_schema_extra = {
        'association': {
            'mappedBy': mappedBy,
        }
    }

    if filteredBy:
        json_schema_extra['association']['filteredBy'] = filteredBy

    if 'json_schema_extra' in kwargs:
        existing_extra = kwargs.pop('json_schema_extra')
        json_schema_extra.update(existing_extra)

    return Field(**kwargs, json_schema_extra=json_schema_extra)    


class Ref(BaseModel, Generic[T]):
    entityType: Type[T]
    instance: Optional[T]
    uuid: Optional[UUID4Str]
    def get_instance(self) -> T:
        if self.instance is None:
            self.instance = {'uuid': self.uuid, 'name': 'C-123'}  # Replace with actual instance retrieval
        return self.instance


class Category(JelloEntity):
    name: Readonly[str]
    description: Optional[str] = None
    parent: Optional[Ref[Category]] = None
    products: Association[Product] = association(mappedBy='category_ref')
    cheapestInCategory: Association[Product] = association(mappedBy='category',filteredBy="price<99")


class Product(JelloEntity):
    name: str
    description: Optional[str] = None
    price: float
    category_embedded: Category
    category_ref: Ref[Category]


    
if __name__ == '__main__':

    print("category name field metadata:")
    field = Category.model_fields['name']
    print(json.dumps(field.json_schema_extra, indent=2))

    print("\ncategory ref metadata:")
    field = Product.model_fields['category_ref']
    entityType = get_args(field.annotation)[0].__name__
    print(f"entityType: {entityType}")

    
    print("\ncheapestInCategory Association metadata:")
    field = Category.model_fields['cheapestInCategory']
    association_info = {
        "entityType": get_args(field.annotation)[0].__name__,  # Get the generic type argument (Product)
        "mappedBy": field.json_schema_extra['association']['mappedBy'],
        "filteredBy": field.json_schema_extra['association']['filteredBy']
    }
    print(json.dumps(association_info, indent=2))


    print("\nCategory schema:")
    print(json.dumps(Category.model_json_schema(), indent=2))


