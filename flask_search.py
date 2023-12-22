
import mysql.connector
from flask import Flask, render_template

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

@app.route('/')
def job_listing():
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)

    # 假設您的表名為 'jobs'，並且有相應的列
 
    # try:
        # 假設您的表名為 'jobs'，並且有相應的列
    cursor.execute("SELECT title, company_name, job_description, salary_range, address, other_info FROM jobs;")
    job_data = cursor.fetchone()
    print(job_data)
    # finally:
    cursor.close()
    conn.close()

    return render_template('job_listing.html', job=job_data)

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=80, debug=True)
