from config import db
from bson import ObjectId
import bcrypt

users_collection = db.users

class User:
    @staticmethod
    def create_user(user_id, password, user_name, jungle_code):
        """새로운 사용자 생성 (비밀번호 해싱 추가)"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user = {
            'user_id': user_id,
            'password': hashed_password,  # 해싱된 비밀번호 저장
            'user_name': user_name,
            'jungle_code': int(jungle_code) if jungle_code.isnumeric() else None,  # 숫자 검증 추가
        }
        return users_collection.insert_one(user)

    @staticmethod
    def find_by_user_id(user_id):
        #아이디(user_id)로 사용자 찾기/로그인할때 !
        return users_collection.find_one({'user_id': user_id})

    @staticmethod
    def find_by_id(user_id):
        #DB에서 사용자 찾을 때
        try:
            return users_collection.find_one({'_id': ObjectId(user_id)})
        except:
            return None  # 유효하지 않은 ObjectId 처리
