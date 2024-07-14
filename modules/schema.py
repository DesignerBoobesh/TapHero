from pydantic import root_validator
from models.helpers import MongoBaseModel
from custom_errors import *
from modules.constants import *
import re
from typing import Optional

class CreateItemParams(MongoBaseModel):
    name: str
    description: str
    price: float
    image: Optional[str]
    category: str
    is_active: bool = True

    seller_mail: Optional[str]
    seller_phone: Optional[str]
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

    @root_validator(pre=True)
    def check(cls, values):
        print("values")
        try:
            values["price"] = float(values["price"])
            if values["price"] < 0: raise
        except:
            print("denemeparams2")
            raise InvalidPrice
        values["name"] = values["name"].strip()
        if values["name"] == "":
            print("denemeparams3")
            print("name")
            raise InvalidName
        if values["category"] not in get_ctype_elems(ItemCategory):
            print("denemeparams5")
            print(values["category"])
            raise InvalidCategory
        if values.get("image"):
            
            if check_is_valid_url(values.get("image")) is False:
                values["image"]="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1200px-Bitcoin.svg.png"
                print("denemeparams6")
                print("image")
                #raise InvalidUrl
        else:
            values["image"]="https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1200px-Bitcoin.svg.png"

        #print(values)
        return values

def check_is_valid_url(url: str):
    url_pattern = re.compile(r'^https?://')
    return url_pattern.match(url)