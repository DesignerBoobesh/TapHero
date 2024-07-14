from models.base_queries import BaseQueryOps
from typing import Optional
from pymongo.client_session import ClientSession
from pymongo.database import Database
from models.base_queries import BaseQueryOps
from models.review.base import Review

class ReviewQueryOps(BaseQueryOps):
    def __init__(self, db: Database, session: Optional[ClientSession] = None) -> Optional[Review]:
        super().__init__(db, Review, session)
    
    def find_one(self, user_name: str, item_name: str):
        result =  self.collection.find_one({"user": user_name, "item": item_name})
        if result:
            return Review.parse_obj(result)
        else:
            return None

    def delete_item_reviews(self, item: str, user_query_ops):
        reviews = self.search({"item": item})
        for review in reviews:
            username = review.user
            self.delete(review.id)
            user_query_ops.update_avg_rating(username, review_query_ops=self)
    
    def delete_user_reviews(self, username: str, item_query_ops):
        reviews = self.search({"user": username})
        for review in reviews:
            item_name = review.item
            self.delete(review.id)
            item_query_ops.update_avg_rating(item_name, review_query_ops=self)
