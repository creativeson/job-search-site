import mysql.connector
from flask import Flask, render_template, request

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
            print(f'Searching for: {query}')
    return render_template('index.html')


@app.route('/result')
def result():
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)
    try:
        # Execute the SQL query
        query = """
        SELECT url, title, 
           CONCAT(LEFT(job_description, 100),"...") AS job_description, 
           new_random_string
            FROM jobs_backup
            LIMIT 10;
        """
        cursor.execute(query)

        # Fetch all rows from the query
        rows = cursor.fetchall()

        # Format the results
        results = []
        for row in rows:
            result = {"url": row[0], "title": row[1], "description": row[2], "new_random_string": row[3]}
            results.append(result)

        print(results)
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")

    finally:
        # Close the connection
        cursor.close()
        conn.close()

    # results = [ {"url": "https://free.com.tw/diffchecker/", "title": "new stuff - 在線文本對比工具", "description": "使用
    # DiffChecker，您可以快速比較兩段文本的差異。"}, ]
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
