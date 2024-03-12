# import mysql.connector
from mysql.connector import connect, Error
from flask import Flask, render_template, request, redirect, url_for
from sys import path
import asyncio
import redis
import datetime
import math, random
import re


path.append('./job-algor/count')
#path.append('../job-algor/count')
from text_to_job import recommend_custom
# from url_to_job import recommend_more

path.append('./job-algor/tfidf')
#path.append('../job-algor/tfidf')
# from tfidf_text_to_job import recommend_custom_tfidf
from tfidf_url_to_job import recommend_more_tfidf


# sys.path.append('../job-algor/count')
# sys.path.append('/root/fantasticJobSite/job-algor/count')
# from job_algor.text_to_job import recommend_custom
# from job_algor.url_to_job import recommend_more



app = Flask(__name__)
redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 數據庫配置
config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'combined_data'
}


# 建立數據庫連接
def get_db_connection():
    conn = connect(**config)
    return conn

@app.route('/about')
def about():
    return render_template('about.html')

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

    return render_template('register.html')


@app.route('/')
def index():
    #morejobs = None
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)
    #job_data = None  # Initialize job_data to None or a suitable default value

    try:
        cursor.execute(
            '''SELECT url
            FROM combined where 
            parse_date = (SELECT MAX(parse_date) FROM combined );''')
        url_data = cursor.fetchall()

        # 檢查 url_data 是否為空值
        if url_data:
            # 從 url_data 中隨機選擇
            selected_url = random.choice(url_data)[0]  
        else:
            print("没有找到任何URL")
        # recommend more job base on the current url
     
        print(selected_url)
        morejobs = recommend_more_tfidf(selected_url)
        print("index.html中利用url more job的第一筆資料",morejobs[0])
        print("共有幾筆資料",len(morejobs))

    except Error as err:
        print(f"MySQL Error: {err}")

    finally:
        cursor.close()
        conn.close()
    # if request.method == 'GET':
    #     query = request.args.get('query', '')  # Retrieve the query parameter

    #     if query:  # Check if the query is not empty
    #         return redirect(url_for('result'))  # Redirect to /result with query
    # return render_template('index.html')
    query = request.args.get('query', '')  # Retrieve the query parameter
    if query:  # Check if the query is not empty
        return redirect(url_for('result'))  # Redirect to /result with query
    return render_template('index.html', morejobs=morejobs)


@app.route('/result', methods=['GET'])
async def result():
    # 分頁參數
    page = request.args.get('page', 1, type=int)  # 預設為第1頁
    per_page = 20  # 每頁顯示20個項目

    upper_bound_salary = request.args.get('upper_bound_salary', '')
    salary = request.args.get('salary', '')
    query = request.args.get('query', '')

    # 生成不包含頁碼的快取鍵
    cache_key = f"{query}:{salary}:{upper_bound_salary}"

    # 嘗試獲取快取的結果集
    cached_results = redis_conn.get(cache_key)
    if cached_results:
        print(f"找到整個結果集的快取 {cache_key}")
        results = eval(cached_results)  # 使用更安全的反序列化方法是更好的選擇
    else:
        # 如果沒有快取，則調用函數獲取結果，並快取整個結果集
        if query:
            results = await asyncio.to_thread(recommend_custom, query, salary, upper_bound_salary)
            redis_conn.set(cache_key, str(results), ex=3600)  # 快取整個結果集
        else:
            results = []

    total_results = len(results)
    total_pages = math.ceil(total_results / per_page)  # 計算總頁數

    # 計算當前頁顯示的資料範圍
    start = (page - 1) * per_page
    end = start + per_page
    page_results = results[start:end]

    return render_template(
        'search_result.html',
        results=page_results,
        total_pages=total_pages,
        current_page=page,
        query=query,
        salary=salary,
        upper_bound_salary=upper_bound_salary
    )



@app.route('/job_content/<new_random_string>')
def job_listing(new_random_string):
    morejobs = None
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)
    job_data = None  # Initialize job_data to None or a suitable default value

    try:
        cursor.execute(
            '''SELECT title, company_name, job_description, 
            salary_range, address, other_info, url, parse_date 
            FROM combined where new_random_string = %s AND 
            parse_date = (SELECT MAX(parse_date) FROM combined );''', (new_random_string,))
        job_data = cursor.fetchone()
        # recommend more job base on the current url
        url = job_data[6]
        print(url)
        morejobs = recommend_more_tfidf(url)
        print("利用url more job的第一筆資料",morejobs[0])

    except Error as err:
        print(f"MySQL Error: {err}")

    finally:
        cursor.close()
        conn.close()
    return render_template('job_listing.html', job=job_data, morejobs=morejobs)

def filter_html_tags(text):
  """
  濾掉 HTML 標籤
  """
  pattern = re.compile(r'<.*?>')
  return pattern.sub('', text)
# from jieba import lcut

@app.route('/company/<company_name>')
def company(company_name):
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)
    company_data = None  # Initialize job_data to None or a suitable default value
    try:
        cursor.execute(
            '''SELECT title, company_name, job_description, 
            salary_range, LEFT(address, 6) AS place, new_random_string, parse_date  
            FROM combined where company_name= %s AND 
            parse_date = (SELECT MAX(parse_date) FROM combined );''', (company_name,))
        company_data = cursor.fetchall()
        print(company_data)
        jobs = []
        for i in company_data:
            job_row = i
            # Check if the row itself is not None
            if job_row is not None:
                job_description = job_row[2] if job_row[2] is not None else """No job 
                description available"""
            else:
                job_description = "No job description available"

            # Check if job_description is not None before slicing
            description = filter_html_tags(job_description[:120]) + "..." if job_description is not None else "..."

            # Create a dictionary with the relevant information
            result = {
                "title": job_row[0],
                'company_name': job_row[1],
                "description": description,
                "new_random_string": job_row[-2],
                "place": job_row[-3],
                "salary_range": job_row[-4],
                "parse_date": job_row[-1],
            }
            # Append the dictionary to the results list
            jobs.append(result)
    except Error as err:
        print(f"MySQL Error: {err}")

    finally:
        cursor.close()
        conn.close()
    return render_template('company.html', companys=jobs)


if __name__ == '__main__':
    import psutil
    print(f"mem size of for loop before: {psutil.Process().memory_info().rss / 1024 / 1024}")
    app.run(host="0.0.0.0", port=5050)
    #app.run(host="0.0.0.0", port=5050 , debug=True)

    print(f"mem size of for loop after: {psutil.Process().memory_info().rss / 1024 / 1024}")
    #
