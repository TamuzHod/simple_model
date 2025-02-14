from typing import TypeVar, Generic, List, Optional, Tuple, Any, Dict
from bson import ObjectId
from database import Database

T = TypeVar('T')

class CursorPagination(Generic[T]):
    def __init__(
        self,
        collection_name: str,
        model_class: type[T],
        field_mappings: Dict[str, str]
    ):
        self.collection_name = collection_name
        self.model_class = model_class
        self.field_mappings = field_mappings
        
    async def paginate(
        self,
        first: Optional[int] = None,
        after: Optional[str] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        order_by: Optional[Dict[str, str]] = None
    ) -> Tuple[List[T], bool]:
        db = Database.get_db()
        collection = getattr(db, self.collection_name)
        query = {}

        if after:
            query['_id'] = {'$gt': ObjectId(after)}

        if filter_params:
            for key, value in filter_params.items():
                if value is not None:
                    mapped_key = self.field_mappings.get(key, key)
                    if key.endswith('_contains'):
                        base_key = mapped_key.replace('_contains', '')
                        query[base_key] = {'$regex': value, '$options': 'i'}
                    else:
                        query[mapped_key] = value

        sort_params = [('_id', 1)]
        if order_by:
            field = self.field_mappings.get(order_by['field'], order_by['field'])
            direction = 1 if order_by['direction'] == 'ASC' else -1
            sort_params = [(field, direction)]

        limit = first or 10
        cursor = collection.find(query).sort(sort_params).limit(limit + 1)
        results = await cursor.to_list(length=limit + 1)

        has_next_page = len(results) > limit
        if has_next_page:
            results = results[:-1]

        return results, has_next_page