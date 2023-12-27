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

    # Execute the SQL query
    query = """
    SELECT url, title, 
       CONCAT(LEFT(job_description, 100),"...") AS job_description
        FROM jobs
        LIMIT 10;
    """
    cursor.execute(query)

    # Fetch all rows from the query
    rows = cursor.fetchall()

    # Format the results
    results = []
    for row in rows:
        result = {"url": row[0], "title": row[1], "description": row[2]}
        results.append(result)

    print(results)

    # Close the connection
    cursor.close()
    conn.close()

    # results = [
    #     {"url": "https://free.com.tw/diffchecker/", "title": "new stuff - 在線文本對比工具", "description": "使用 DiffChecker，您可以快速比較兩段文本的差異。"},
    #     {"url": "https://free.com.tw/diffnow/", "title": "DiffNow - 立即比較文本、文件和目錄", "description": "DiffNow 允許您比較內容，包括文本和文件夾，簡單易用。"},
    #     # 添加更多資料，直到達到 10 筆
    #     # ...
    # ]
    return render_template('search_result.html', results=results)


@app.route('/')
def job_listing():
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)

    # 假設您的表名為 'jobs'，並且有相應的列
    try:
        # 假設您的表名為 'jobs'，並且有相應的列
        cursor.execute(
            "SELECT title, company_name, job_description, salary_range, address, other_info, url FROM jobs limit 1 offset 2;")
        job_data = cursor.fetchone()
        print(job_data)
    finally:
        cursor.close()
        conn.close()
    return render_template('job_listing.html', job=job_data)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
