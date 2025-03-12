from flask import Flask, render_template
from controllers.user_controller import user_bp
from controllers.study_controller import study_bp
import config

app = Flask(__name__)

#  환경 설정 적용 (MongoDB, 세션 설정 등)
app.config.from_object(config)

app.register_blueprint(user_bp)
app.register_blueprint(study_bp)

# 홈페이지 라우트
@app.route('/')
def home():
   return render_template('login.html')

if __name__ == '__main__':
      app.run('0.0.0.0', port=5001, debug=True)



