# import mysql.connector
from mysql.connector import connect
from flask import Flask, render_template, request, redirect, url_for
from sys import path

path.append('./job-algor/count')
# sys.path.append('../job-algor/count')
# sys.path.append('/root/fantasticJobSite/job-algor/count')
# from job_algor.text_to_job import recommend_custom
# from job_algor.url_to_job import recommend_more
from text_to_job import recommend_custom
from url_to_job import recommend_more


app = Flask(__name__)

# 數據庫配置
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'job_data'
}


# 建立數據庫連接
def get_db_connection():
    conn = connect(**config)
    return conn


@app.route('/register', methods=['GET', 'POST'])
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
        conn = mysql.connector.connect(**config)
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

    return render_template('register.html')


@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        query = request.args.get('query', '')  # Retrieve the query parameter

        if query:  # Check if the query is not empty
            # print(f'Searching for: {query}')
            return redirect(url_for('result'))  # Redirect to /result with query
    return render_template('index.html')


# @app.route('/result', methods=['GET'])
# def result():
    # if request.method == 'GET':

    #     salary = request.args.get('salary', '')
    #     print(salary)

    #     selected_districts = request.args.getlist('district')
    #     print(selected_districts)
    #     query = request.args.get('query', '')  # Retrieve the query parameter
    #     if query:  # Check if the query is not empty
    #         results = recommend_custom(query, selected_districts ) if query else []
    #         return render_template('search_result.html', results=results)
    # query = request.args.get('query', '')  # Retrieve the query parameter
    # results = recommend_custom(query) if query else []
    # return render_template('search_result.html', results=results)
@app.route('/result', methods=['GET'])
def result():
    upper_bound_salary = request.args.get('upper_bound_salary', '')
    print(upper_bound_salary)

    salary = request.args.get('salary', '')
    print(salary)

    selected_districts = request.args.getlist('district')
    print(selected_districts)

    query = request.args.get('query', '')  # Retrieve the query parameter
    if query:  # Check if the query is not empty
        results = recommend_custom(query, salary, upper_bound_salary)
    else:
        results = []

    return render_template('search_result.html', results=results)



@app.route('/job_content/<new_random_string>')
def job_listing(new_random_string):
    global morejobs
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)
    job_data = None  # Initialize job_data to None or a suitable default value

    try:
        # 假設您的表名為 'jobs'，並且有相應的列
        cursor.execute(
            '''SELECT title, company_name, job_description, 
            salary_range, address, other_info, url 
            FROM combined_site_feature where new_random_string = %s;''', (new_random_string,))
        job_data = cursor.fetchone()
        # recommend more job base on the current url
        url = job_data[6]
        print(url)
        morejobs = recommend_more(url)
        print(morejobs)

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")

    finally:
        cursor.close()
        conn.close()
    return render_template('job_listing.html', job=job_data, morejobs=morejobs)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
