from modules.auth.schema import *
from models.user.queries import *
from pymongo.client_session import ClientSession
from pymongo.database import Database
import bcrypt

def validate_and_get_user(auth_login_params: AuthLoginParams, mongo_db: Database, mongo_session: Optional[ClientSession]):
    user_query_ops = UserQueryOps(mongo_db, mongo_session)
    user = user_query_ops.get_by_username(auth_login_params.username)

    if bcrypt.checkpw(auth_login_params.password, user.password):
        return user
    else:
        raise InvalidPassword
