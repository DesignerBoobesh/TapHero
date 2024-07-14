from bson import ObjectId
from pydantic import BaseModel, Extra

class PydanticObjectId(ObjectId):
    """
    ObjectId not directly supported by pydantic. So this class will help us both
    serialization and validation
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class MongoBaseModel(BaseModel):
    """
    This model will be used in this project globally. This way we can change default
    configuration of pydantic.BaseModel
    The most important thing is we turn ObjectId into string. This way we can use ObjectId in json
    """
    class Config:
        extra = Extra.ignore  # ignores extra parameters when initializing model
        allow_population_by_field_name = True  # this will allow population by alias
        json_encoders = {
            ObjectId: lambda v: str(v)  # ObjectId will be encoded as string
        }

    def update_fields(self, update_params: dict):
        fields = self.dict()
        fields.update(update_params)
        return self.parse_obj(fields)