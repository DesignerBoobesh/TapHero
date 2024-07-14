from typing import List, Optional, Type
from pymongo.database import Database
from pymongo.collection import ReturnDocument
from pymongo.client_session import ClientSession
from pydantic import BaseModel
from models.helpers import PydanticObjectId

class BaseQueryOps:
    def __init__(self,
                 db: Database,
                 model: Type[BaseModel],
                 session: Optional[ClientSession] = None):
        self.collection = db.get_collection(model.get_collection_name())
        self.model = model
        self.session = session

    def create(self, document: BaseModel) -> BaseModel:
        # Exclude fields with None values
        excluded_fields = {k: v for k, v in document.dict(by_alias=True, exclude={'id'}).items() if v is not None}
        
        new_document = self.collection.insert_one(excluded_fields, session=self.session)
        document.id = new_document.inserted_id
        return self.model.parse_obj(document)

    def update(self, document: BaseModel) -> BaseModel:
        updated_fields = document.dict(by_alias=True, exclude_none=True, exclude={'id'})
        updated_document = self.collection.find_one_and_update(
            {'_id': document.id},
            {'$set': updated_fields},
            upsert=True,
            return_document=ReturnDocument.AFTER,
            session=self.session
        )
        return self.model.parse_obj(updated_document)

    def search(self,
               search_filter: dict,
               sort_options: List[tuple] = None,
               limit: Optional[int] = None) -> List[BaseModel]:
        search_filter = search_filter if search_filter is not None else {}
        search_filter.update(search_filter)
        sort_options = sort_options if sort_options is not None else []
        result = self.collection.find(search_filter,
                                      sort=sort_options,
                                      session=self.session)
        if limit:
            result = result.limit(limit)
        return [self.model.parse_obj(r) for r in result]

    def delete(self, document_id: str):
        self.collection.delete_one({'_id': PydanticObjectId(document_id)}, session=self.session)