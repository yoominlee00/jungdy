from config import db
import datetime
from bson import ObjectId

studies_collection = db.studies  # MongoDB 컬렉션

class Study:
    
    @staticmethod
    def create_study(study_name, category, study_date, start_time, end_time, location, max_participants, creator_id, study_content):
        """새로운 스터디 생성"""
        
        study_date_obj = datetime.datetime.strptime(study_date, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)
        start_time_obj = datetime.datetime.strptime(f"{study_date} {start_time}", '%Y-%m-%d %H:%M').replace(tzinfo=datetime.timezone.utc)
        end_time_obj = datetime.datetime.strptime(f"{study_date} {end_time}", '%Y-%m-%d %H:%M').replace(tzinfo=datetime.timezone.utc)

        study = {
            'study_name': study_name,  
            'category': category,  
            'study_date': study_date_obj,  
            'start_time': start_time_obj,  
            'end_time': end_time_obj,  
            'location': location,  
            'max_participants': max_participants,  
            'current_participants': 0,  
            'participants': [],  
            'creator_id': ObjectId(creator_id),  
            'created_at': datetime.datetime.utcnow(),  
            'study_content': study_content  
        }

        return studies_collection.insert_one(study)

    @staticmethod
    def find_by_category_and_date(category, date):
        """카테고리와 날짜를 기준으로 스터디 조회 (날짜 & 시간 정렬)"""
        return list(studies_collection.find({
            'category': category,
            'study_date': {'$gte': date}
        }).sort([('study_date', 1), ('start_time', 1)]))

    @staticmethod
    def find_by_id(study_id):
        """스터디 ID로 조회"""
        return studies_collection.find_one({'_id': ObjectId(study_id)})

    @staticmethod
    def join_study(study_id, user_id):
        """스터디 참가"""
        study = studies_collection.find_one({'_id': ObjectId(study_id)})
        if not study:
            return False, "스터디를 찾을 수 없습니다."

        if ObjectId(user_id) in study['participants']:
            return False, "이미 참여 중입니다."

        if study['current_participants'] >= study['max_participants']:
            return False, "스터디 인원이 가득 찼습니다."

        studies_collection.update_one(
            {'_id': ObjectId(study_id)},
            {
                '$push': {'participants': ObjectId(user_id)},
                '$inc': {'current_participants': 1}
            }
        )
        return True, "참여 성공!"

    @staticmethod
    def find_studies_i_joined(user_id):
        """내가 참여 중인 스터디 조회"""
        return list(studies_collection.find({
            'participants': ObjectId(user_id)
        }))

    @staticmethod
    def update_study(study_id, user_id, updates):
        """스터디 수정 (방장만 가능)"""
        study = studies_collection.find_one({'_id': ObjectId(study_id)})
        if not study:
            return False, "스터디를 찾을 수 없습니다."

        if study['creator_id'] != ObjectId(user_id):
            return False, "수정 권한이 없습니다."

        studies_collection.update_one(
            {'_id': ObjectId(study_id)},
            {'$set': updates}
        )
        return True, "수정 완료!"

    @staticmethod
    def delete_study(study_id, user_id):
        """스터디 삭제 (방장만 가능)"""
        study = studies_collection.find_one({'_id': ObjectId(study_id)})
        if not study:
            return False, "스터디를 찾을 수 없습니다."

        if study['creator_id'] != ObjectId(user_id):
            return False, "삭제 권한이 없습니다."

        studies_collection.delete_one({'_id': ObjectId(study_id)})
        return True, "삭제 완료!"
