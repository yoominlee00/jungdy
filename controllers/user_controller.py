from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from models.user_model import User
import bcrypt

user_bp = Blueprint('user', __name__)

# 회원가입
@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        user_name = request.form['user_name']
        jungle_code = request.form['jungle_code']

        # 아이디 중복 확인
        if User.find_by_user_id(user_id):
            flash("이미 존재하는 아이디입니다.", "danger")
            return redirect(url_for('user.signup'))

        # 비밀번호 해싱 적용
        User.create_user(user_id, password, user_name, jungle_code)
        flash("회원가입이 완료되었습니다. 로그인하세요!", "success")
        return redirect(url_for('user.login'))

    return render_template('signup.html')

# 로그인
@user_bp.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:  # 이미 로그인한 경우, 메인 화면으로 리디렉션
        return redirect(url_for('study.home'))  #'study.home'이 존재하는지 확인 필요!
     
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        user = User.find_by_user_id(user_id)

        if not user:
            flash("존재하지 않는 아이디입니다.", "danger")  # ✅ "danger"로 설정하여 프론트와 일관성 유지
            return redirect(url_for('user.login'))

        # 비밀번호 검증
        if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            flash("아이디 또는 비밀번호가 틀렸습니다.", "danger")  # ✅ "danger"로 설정
            return redirect(url_for('user.login'))

        # 로그인 성공
        session['user_id'] = str(user['_id'])  # ✅ 세션 저장
        session.permanent = True  # ✅ 세션 유지 설정
        flash("로그인 성공!", "success")  # ✅ 성공 시 "success" 설정
        return redirect(url_for('study.home'))  # ✅ 'study.home'이 존재하는지 확인 필요!

    return render_template('login.html')



@user_bp.route('/mypage', methods=['GET'])
def mypage():
    if 'user_id' not in session:
        flash("로그인이 필요합니다.", "danger")
        return redirect(url_for('user.login'))  # 로그인 페이지로 이동

    user_id = session['user_id']
    user = User.find_by_id(user_id)

    if not user:
        flash("사용자 정보를 찾을 수 없습니다.", "danger")
        return redirect(url_for('user.login'))

    return render_template('mypage.html', user=user)  # mypage.html 렌더링


@user_bp.route('/logout')
def logout():
    session.pop('user_id', None)  # 세션에서 user_id 삭제
    flash("로그아웃 되었습니다.", "info")
    return redirect(url_for('user.login'))
