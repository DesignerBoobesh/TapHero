from pydantic import Field, root_validator
from typing import Optional
from models.helpers import PydanticObjectId, MongoBaseModel
from pymongo.database import Database
from pymongo.errors import CollectionInvalid
from custom_errors import RangeError, LongTextError

class Review(MongoBaseModel):
    __collection_name__: str = 'review'
    id: Optional[PydanticObjectId] = Field(None, alias='_id')
    user: str
    item: str
    review: str
    rating: int

    @root_validator(pre=True)
    @classmethod
    def check(cls, values):
        if len(values.get("review", "")) > 140:
            raise LongTextError
        if int(values["rating"]) > 5 or int(values["rating"]) < 1:
            raise RangeError
        return values

    @classmethod
    def get_collection_name(cls):
        return cls.__collection_name__

def create_collection(db: Database):
    try:
        db.create_collection("review", {})
    except CollectionInvalid:  # collection already exists
        pass
    # Make unique indexes
    db.user.create_index("user", unique=False)
    db.user.create_index("item", unique=False)
