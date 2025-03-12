from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from models.study_model import Study
import datetime
from bson import ObjectId

study_bp = Blueprint('study', __name__)


@study_bp.route('/study')
def home():
    category = request.args.get('category', 'frontend')
    
    # URL에서 'date' 값을 가져오고, 없으면 today를 사용
    date_str = request.args.get('date')
    if not date_str:  # URL에 날짜가 없으면 오늘 날짜로 설정
        date_str = datetime.datetime.today().strftime('%Y-%m-%d')
    else:
        # 혹시 다른 형식으로 넘어올 경우 YYYY-MM-DD로 변환
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            date_str = date_obj.strftime('%Y-%m-%d')  # 다시 올바른 형식으로 변환
        except ValueError:
            date_str = datetime.datetime.today().strftime('%Y-%m-%d')  # 잘못된 값이면 today로 설정

    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=datetime.timezone.utc)
    prev_date = (date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    studies = Study.find_by_category_and_date(category, date)
    user_id = session.get('user_id')

    for study in studies:
        study['_id'] = str(study['_id'])
        study['participation_status'] = Study.get_participation_status(study, user_id)

    return render_template(
        'study.html', category=category, studies=studies, today=date_str, prev_date=prev_date, next_date=next_date
    )


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

        success, message = Study.create_study(study_name, category, study_date, start_time, end_time, location, max_participants, creator_id, study_content)
        if not success:
            flash(message, "danger")
            return redirect(url_for('study.create_study'))  # 실패 시 다시 생성 페이지로 이동

        flash("스터디가 성공적으로 생성되었습니다.", "success")
        return redirect(url_for('study.home'))

    return render_template('create_study.html')

# 스터디 참가
@study_bp.route('/study/<study_id>/join', methods=['POST'])
def join_study(study_id):
    user_id = session.get('user_id')  
    if not user_id:
        return redirect(url_for('user.login'))

    success, message = Study.join_study(study_id, user_id)
    flash(message, "success" if success else "danger")

    return redirect(url_for('study.home'))

# 스터디 수정
@study_bp.route('/study/<study_id>/edit', methods=['POST'])
def edit_study(study_id):
    session_user_id = session.get('user_id')  # 현재 로그인한 사용자 ID 가져오기
    if not session_user_id:
        return redirect(url_for('user.login'))

    updates = {
        "study_name": request.form["study_name"],
        "category": request.form["category"],
        "study_date": request.form["study_date"],
        "start_time": request.form["start_time"],
        "end_time": request.form["end_time"],
        "location": request.form["location"],
        "max_participants": int(request.form["max_participants"]),
        "study_content": request.form["study_content"]
    }

    Study.update_study(study_id, session_user_id, updates)

    return redirect(url_for('study.home'))

# 스터디 삭제 (방장만 가능)
@study_bp.route('/study/<study_id>/delete', methods=['POST'])
def delete_study(study_id):
    session_user_id = session.get('user_id')  # 현재 로그인한 사용자 ID 가져오기
    if not session_user_id:
        return redirect(url_for('user.login'))  # 로그인 안 한 경우 차단

    success, message = Study.delete_study(study_id, session_user_id)  # 스터디 삭제 함수 실행

    return redirect(url_for('study.home'))  # 삭제 후 메인 페이지로 이동


#스터디 탈퇴 (참가자가 탈퇴 가능)
@study_bp.route('/study/<study_id>/leave', methods=['POST'])
def leave_study(study_id):
    session_user_id = session.get('user_id')  # 현재 로그인한 사용자 ID 가져오기
    if not session_user_id:
        return redirect(url_for('user.login'))  # 로그인 안 한 경우 차단

    success = Study.leave_study(study_id, session_user_id)  # 스터디 탈퇴 함수 실행

    return redirect(url_for('study.home'))  # 탈퇴 후 메인 페이지로 이동


