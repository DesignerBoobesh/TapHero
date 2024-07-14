from pydantic import root_validator, Field
from typing import Optional
from models.helpers import PydanticObjectId, MongoBaseModel
from pymongo.database import Database
from pymongo.errors import CollectionInvalid
import bcrypt
from os import environ
from typing import List

class User(MongoBaseModel):
    __collection_name__: str = 'user'
    id: Optional[PydanticObjectId] = Field(None, alias='_id')
    email: str
    username: str
    password: bytes
    favorite_list: List[str] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] # List of item IDs


    money: float = 0.0

    @classmethod
    def get_collection_name(cls):
        return cls.__collection_name__

def create_collection(db: Database):
    try:
        db.create_collection("user", {})
    except CollectionInvalid:  # collection already exists
        pass
    # Make unique indexes
    db.user.create_index("username", unique=True)
    db.user.create_index("email", unique=True)
    db.user.insert_one({ "email":"admin@gmail.com", # Create admin user
                            "username":"admin", 
                            "password": bcrypt.hashpw(environ.get("ADMIN_PASS").encode("utf-8"), bcrypt.gensalt())
                        })
