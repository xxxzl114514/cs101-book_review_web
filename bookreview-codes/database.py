#本网站相关的数据库连接和操作的函数

import mysql.connector

#建立数据库连接
def database_connect():
    conn = mysql.connector.connect(
        host = 'localhost',
        user = 'root',
        password = '123456',
        database = 'bookreview'
    )
    return conn

#创建数据表
def create_table():
    # 连接
    conn = database_connect()
    cursor = conn.cursor()
    #将取出的数据当做字典使用的方法 ：cursor = conn.cursor(cursor_class = mysql.connector.cursor.MySQLCursorDict) 
    # 创建数据表users、books、reviews、ratings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            question VARCHAR(255) NOT NULL,
            answer VARCHAR(255) NOT NULL,
            profilepath VARCHAR(255) DEFAULT 'default.jpg',
            bio VARCHAR(255) DEFAULT '-'
        )
    """
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255) NOT NULL,
            profile TEXT,
            coverpath VARCHAR(255) NOT NULL,
            isbn VARCHAR(255) NOT NULL UNIQUE,
            user_id INT,
            user_name VARCHAR(255),
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            content TEXT NOT NULL,
            rating INT CHECK (rating BETWEEN 1 AND 5),
            book_id INT,
            user_id INT,
            user_name VARCHAR(255),
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE, 
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """
    )
    # 关闭cursor和conn
    cursor.close()
    conn.close()