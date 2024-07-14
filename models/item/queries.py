from models.base_queries import BaseQueryOps
from typing import List, Optional
from pymongo.client_session import ClientSession
from pymongo.database import Database
from models.base_queries import BaseQueryOps
from models.item.base import Item
from modules.schema import CreateItemParams
from models.review.queries import ReviewQueryOps

class ItemQueryOps(BaseQueryOps):
    def __init__(self, db: Database, session: Optional[ClientSession] = None):
        super().__init__(db, Item, session)
    
    def get_by_name(self, name: str) -> Optional[Item]:
        result =  self.collection.find_one({"name": name})
        return self.model.parse_obj(result)
    
    def update_with_params(self, create_item_params: CreateItemParams):
        item = self.get_by_name(create_item_params.name)
        updated_fields = create_item_params.dict(exclude_unset=True)  # Exclude fields with None values
        item.update_fields(updated_fields)
        self.update(item)

    def delete_by_name(self, name: str):
        self.collection.delete_one({"name": name})

    def update_avg_rating(self, item_name: str, review_query_ops: ReviewQueryOps):
        item = self.get_by_name(item_name)
        item_reviews = review_query_ops.search({'item': item_name})

        if len(item_reviews) > 0:
            item.avg_rating = sum([review.rating for review in item_reviews]) / len(item_reviews)
        else: 
            item.avg_rating = 0
       
        self.update(item)
