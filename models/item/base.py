from pydantic import root_validator, Field
from typing import Optional
from models.helpers import PydanticObjectId, MongoBaseModel
from pymongo.database import Database
from pymongo.errors import CollectionInvalid
from custom_errors import *
from modules.constants import *

class Item(MongoBaseModel):
    __collection_name__: str = 'item'
    id: Optional[PydanticObjectId] = Field(None, alias='_id')
    name: str
    description: str
    price: float
    is_active: bool = True
    seller_mail: Optional[str]
    seller_phone: Optional[str]
    image: Optional[str]
    category: str

    #vehicle
    type_vehicle: Optional[str]
    year_vehicle: Optional[str]
    brand_vehicle: Optional[str]
    model_vehicle: Optional[str]
    color: Optional[str]
    engine_displacement: Optional[str]
    fuel_type: Optional[str]
    transmission_type: Optional[str]
    mileage: Optional[str]

    #computer
    type_computer: Optional[str]
    year_computer: Optional[str]
    brand_computer: Optional[str]
    model_computer: Optional[str]
    processor_computer: Optional[str]
    ram_computer: Optional[str]
    storage_computer: Optional[str]
    graphics_card: Optional[str]
    operating_system_computer: Optional[str]

    #phone
    operating_system_phone: Optional[str]
    processor_phone: Optional[str]
    ram_phone: Optional[str]
    storage_phone: Optional[str]
    year_phone: Optional[str]
    brand_phone: Optional[str]
    model_phone: Optional[str]
    camera_specifications: Optional[str]
    battery_capacity: Optional[str]

    #privatelesson
    tutor_name: Optional[str]
    lessons: Optional[str]
    location: Optional[str]
    duration: Optional[str]

    @classmethod
    def get_collection_name(cls):
        return cls.__collection_name__

def create_collection(db: Database):
    try:
        db.create_collection("item", {})
    except CollectionInvalid:  # collection already exists
        pass
    # Make unique indexes
    db.user.create_index("name", unique=True)
    #db.user.create_index("seller", unique=False)
