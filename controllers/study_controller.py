from flask import Blueprint, request, render_template, redirect, url_for, session
from models.study_model import Study
import datetime
from bson import ObjectId

study_bp = Blueprint('study', __name__)

# 메인 페이지 (스터디 목록 조회)
@study_bp.route('/study')
def home():
    category = request.args.get('category', 'frontend')  # 기본값: frontend
    date_str = request.args.get('date', datetime.datetime.today().strftime('%Y-%m-%d'))  # 오늘 날짜 기본값
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)

    prev_date = (date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    studies = Study.find_by_category_and_date(category, date)
    user_id = session.get('user_id')

    # 참여 상태 표시
    for study in studies:
        study['_id'] = str(study['_id'])
        study['participation_status'] = get_participation_status(study, user_id)

    return render_template(
        'study.html', category=category, studies=studies, today=date_str, prev_date=prev_date, next_date=next_date
    )

# 참여 상태 확인 함수
def get_participation_status(study, user_id):
    if ObjectId(user_id) in study['participants']:
        return "참여중"
    if study['current_participants'] >= study['max_participants']:
        return "참여마감"
    return "참여하기"

# 스터디 생성
@study_bp.route('/study/create', methods=['GET', 'POST'])
def create_study():
    if request.method == 'POST':
        study_name = request.form['study_name']
        category = request.form['category']
        study_date = request.form['study_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        location = request.form['location']
        max_participants = int(request.form['max_participants'])
        study_content = request.form['study_content']
        creator_id = session.get('user_id')  

        Study.create_study(study_name, category, study_date, start_time, end_time, location, max_participants, creator_id, study_content)
        return redirect(url_for('study.home'))

    return render_template('create_study.html')

# 스터디 참가
@study_bp.route('/study/<study_id>/join', methods=['POST'])
def join_study(study_id):
    user_id = session.get('user_id')  
    if not user_id:
        return redirect(url_for('user.login'))

    success, message = Study.join_study(study_id, user_id)
    if not success:
        return message, 400

    return redirect(url_for('study.home'))

# 내가 참여한 스터디 조회
@study_bp.route('/study/my')
def my_studies():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user.login'))

    studies = Study.find_studies_i_joined(user_id)
    return render_template('my_studies.html', studies=studies)
