# auth.py
from flask import Blueprint, render_template, request, redirect, url_for

auth_bp = Blueprint('auth', __name__, template_folder='templates')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 從表單獲取數據
        user_id = request.form['id']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        name = request.form['name']
        gender = request.form['gender']
        education = request.form['education']
        school = request.form['school']
        experience = request.form['experience']

        # 檢查 ID 是否存在於資料庫
        conn = connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        # 檢查密碼是否匹配和其他驗證...
        # ...

        if user:
            # 使用者ID已存在
            return "ID已存在，請重新輸入"
        else:
            # 註冊用戶
            cursor.execute(
                "INSERT INTO users (id, password, email, name, gender, education, school, experience) VALUES (%s, %s, "
                "%s, %s, %s, %s, %s, %s)",
                (user_id, password, email, name, gender, education, school, experience))
            conn.commit()
            return "註冊成功"

    return render_template('auth/register.html')

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         # 處理登錄請求
#         pass
#     return render_template('auth/login.html')

# @auth_bp.route('/logout')
# def logout():
#     # 處理登出請求
#     pass