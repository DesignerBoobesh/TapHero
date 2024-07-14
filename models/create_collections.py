from pymongo.database import Database
import pymongo
from os import environ

def create_collections(db: Database):

    try:
        from models.user.base import create_collection
        create_collection(db)
    except Exception as e:
        print(e)
    try:
        from models.item.base import create_collection
        create_collection(db)
    except Exception as e:
        print(e)
    try:
        from models.review.base import create_collection
        create_collection(db)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    MONGO_PASS = environ.get('MONGO_PASS')
    mongo_client = pymongo.MongoClient(f"mongodb+srv://ismail:{MONGO_PASS}@hw1.m5wwlop.mongodb.net/?retryWrites=true&w=majority")
    mongo_session = mongo_client.start_session()
    mongo_db = mongo_client.main
    create_collections(mongo_db)

# PYTHONPATH="." python3 models/create_collections.py