from config import db
import datetime
from bson import ObjectId

studies_collection = db.studies  # MongoDB 컬렉션

class Study:


    @staticmethod
    def create_study(study_name, category, study_date, start_time, end_time, location, max_participants, creator_id, study_content):
        """새로운 스터디 생성 (필수 입력값 검증 추가)"""
        if not all([study_name, category, study_date, start_time, end_time, location, max_participants, creator_id, study_content]):
            return False, "모든 정보를 입력해주세요." 

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
            'study_content': study_content  
        }

        studies_collection.insert_one(study)
        return True, "스터디가 성공적으로 생성되었습니다."

    @staticmethod
    def find_by_category_and_date(category, date):
        """카테고리와 날짜를 기준으로 스터디 조회 (날짜 & 시간 정렬)"""
        return list(studies_collection.find({
            'category': category,
            'study_date': {'$eq': date}
        }).sort([('start_time', 1)]))  # 시작 시간 기준 정렬


    @staticmethod
    def get_participation_status(study, user_id):
        """사용자의 참가 상태를 반환"""
        if not user_id:  # 로그인이 안 되어 있는 경우
            return "로그인이 필요합니다"

        user_object_id = ObjectId(user_id)

        if user_object_id in study['participants']:
            return "참여중"

        if study['current_participants'] >= study['max_participants']:
            return "참여마감"

        return "참여하기"
    
    @staticmethod
    def join_study(study_id, user_id):
        """스터디 참가 (participants 리스트에 user_id 추가 및 참여 인원 증가)"""
        user_object_id = ObjectId(user_id)

        # 참가자 추가 및 참여 인원 증가
        studies_collection.update_one(
            {'_id': ObjectId(study_id)},
            {
                '$push': {'participants': user_object_id},
                '$inc': {'current_participants': 1}
            }
        )
        return True  
    

    
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

    
    @staticmethod
    def leave_study(study_id, user_id):
        """스터디 탈퇴 (participants 리스트에서 user_id 제거 및 참여 인원 감소)"""
        user_object_id = ObjectId(user_id)

        # 참가자 제거 및 참여 인원 감소
        studies_collection.update_one(
            {'_id': ObjectId(study_id)},
            {
                '$pull': {'participants': user_object_id},
                '$inc': {'current_participants': -1}
            }
        )
        return True  # 성공 반환



   
