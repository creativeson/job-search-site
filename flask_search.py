import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
import sys
sys.path.append('/home/abu/PycharmProjects/job-algor/count')
from text_to_job import recommend_custom


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
    conn = mysql.connector.connect(**config)
    return conn


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        query = request.args.get('query', '')  # Retrieve the query parameter
        if query:  # Check if the query is not empty
            # print(f'Searching for: {query}')
            return redirect(url_for('result', query=query))  # Redirect to /result with query
    return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'GET':
        query = request.args.get('query', '')  # Retrieve the query parameter
        if query:  # Check if the query is not empty
            results = recommend_custom(query) if query else []
            return render_template('search_result.html', results=results)
    query = request.args.get('query', '')  # Retrieve the query parameter
    results = recommend_custom(query) if query else []
    return render_template('search_result.html', results=results)


@app.route('/job_content/<new_random_string>')
def job_listing(new_random_string):
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)
    job_data = None  # Initialize job_data to None or a suitable default value

    try:
        # 假設您的表名為 'jobs'，並且有相應的列
        cursor.execute(
            '''SELECT title, company_name, job_description, 
            salary_range, address, other_info, url 
            FROM jobs_backup where new_random_string = %s;''', (new_random_string,))
        job_data = cursor.fetchone()

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")

    finally:
        cursor.close()
        conn.close()
    return render_template('job_listing.html', job=job_data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
