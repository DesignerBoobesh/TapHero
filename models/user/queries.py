from models.base_queries import BaseQueryOps
from typing import Optional
from pymongo.client_session import ClientSession
from pymongo.database import Database
from models.base_queries import BaseQueryOps
from models.review.queries import ReviewQueryOps
from models.user.base import User
from custom_errors import UserNotFound

class UserQueryOps(BaseQueryOps):
    def __init__(self, db: Database, session: Optional[ClientSession] = None):
        super().__init__(db, User, session)

    def get_by_username(self, username: str) -> User:
        result = self.collection.find_one({'username': username})
        try:
            return User.parse_obj(result)
        except:
            raise UserNotFound
    
    def delete_by_username(self, username: str):
        self.collection.delete_one({'username': username})
    
    def update_avg_rating(self, user_name: str, review_query_ops: ReviewQueryOps):
        user = self.get_by_username(user_name)
        users_reviews = review_query_ops.search({'user': user_name})
        
        if len(users_reviews) > 0:
            user.avg_rating = sum([review.rating for review in users_reviews]) / len(users_reviews)
        else:
            user.avg_rating = 0
            
        self.update(user)

    def add_to_favorite_list(self, username: str, item_name: str):
        user = self.get_by_username(username)
        if item_name not in user.favorite_list:
            user.favorite_list.append(item_name)
            self.update(user)
    
    def remove_from_favorite_list(self, username: str, item_name: str):
        user = self.get_by_username(username)
        if item_name in user.favorite_list:
            user.favorite_list.remove(item_name)
            self.update(user)