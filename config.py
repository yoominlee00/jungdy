from pymongo import MongoClient
from datetime import timedelta

# MongoDB 연결 설정
#MONGO_URI = "mongodb://yumin606:dldbals606@localhost:27017"


SECRET_KEY = 'your_secret_key'  # 세션 암호화 키
PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 세션 유지 기간 (7일)

client = MongoClient('localhost',27017)
db = client.dbjungle

db.studies.create_index([("study_date", 1)])

