from flask import Flask, render_template, request, url_for, flash, redirect, session, jsonify
from database import database_connect, create_table
from werkzeug.utils import secure_filename
from PIL import Image
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Yggdrasill' #密钥
app.config['COVER_UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static\\covers') #文件的存储路径，用于存储书的封面图片
app.config['USERPROFILE_UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static\\userprofiles') #用于存储用户头像的图片
TARGET_COVER_WIDTH = 270   #封面长宽限制
TARGET_COVER_HEIGHT = 395
TARGET_USERPROFILE_WIDTH = 250   #头像长宽限制
TARGET_USERPROFILE_HEIGHT = 250
MAX_FILE_SIZE = 8 * 1024 * 1024 # means 8MB

#用于测试的主页面
@app.route('/test/')
def test_index():
    return render_template('test_index.html')

# 主页面
@app.route('/')
def index():
    #取用户名
    username = None 
    user_id = None 
    if 'username' in session:
        username = session['username']
        user_id = session['user_id']
    #取书籍列表
    conn = database_connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books ORDER BY RAND() LIMIT 14")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', user_id = user_id, username = username, books = books)

# 刷新书籍
@app.route('/refresh_books', methods=['GET'])
def get_random_books():
    conn = database_connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books ORDER BY RAND() LIMIT 14")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(books)

# 搜索书籍
@app.route('/search_books', methods=['GET'])
def search_books():
    keyword = request.args.get('keyword', '')
    print(f"Searching for keyword: {keyword}")
    conn = database_connect()
    cursor = conn.cursor(dictionary=True)
    if keyword: #有检索，不限制数量
        cursor.execute('''SELECT * FROM books
                          WHERE title LIKE %s OR author LIKE %s OR isbn = %s
                          ORDER BY title''',
                       ('%' + keyword + '%', '%' + keyword + '%', keyword))
    else: #在没有检索的情况下，限制14本
        cursor.execute("SELECT * FROM books ORDER BY RAND() LIMIT 14")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(books)

# 新增书籍
@app.route('/new_book/', methods = ('GET', 'POST'))
def new_book():
    # 查看登录状态，若未登录则跳转到登录页
    if not('username' in session):
        return redirect(url_for("login"))
    user_id = session['user_id']
    user_name = session['username']
    if request.method == 'POST':
        # 从表单中取数据
        title = request.form['title']
        author = request.form['author']
        profile = request.form['profile']
        cover = request.files['cover']
        isbn = request.form['isbn']
        if not profile or len(profile) < 1:
            profile = "-"
        # 连接数据库        
        conn = database_connect()
        cursor = conn.cursor(dictionary=True)
        # 对于新增书籍的合法性检查
        cursor.execute("SELECT * FROM books WHERE isbn = %s", (isbn,))
        book = cursor.fetchone()
        if book:
            flash('ISBN相同的书籍已存在')
        elif len(title) < 1 or len(title) > 255:
            flash('标题长度为1~255')
        elif len(author) < 1 or len(author) > 255:
            flash('作者长度为1~255')
        elif len(profile) > 2000:
            flash('简介长度不能大于2000')
        elif not (len(isbn) == 13):
            flash('ISBN格式错误（需要13位数字）')
        elif not cover:
            flash('需要上传封面文件')
        elif request.content_length > MAX_FILE_SIZE:
            flash('文件太大，无法上传' + ' (限制为' + str(MAX_FILE_SIZE / 1024 / 1024) + 'MB)')
        else:
            # 在服务器保存图片文件
            filepath = ''
            filename = secure_filename('temp_' + isbn + os.path.splitext(cover.filename)[1])    #存放临时文件
            filepath = os.path.join(app.config['COVER_UPLOAD_FOLDER'], filename)
            if not os.path.exists(app.config['COVER_UPLOAD_FOLDER']):   # 不存在对应路径时，生成路径
                os.makedirs(app.config['COVER_UPLOAD_FOLDER']) 
            cover.save(filepath)
            # 缩放图片尺寸
            with Image.open(filepath) as img:
                img = img.resize((TARGET_COVER_WIDTH, TARGET_COVER_HEIGHT))
                filename = secure_filename(isbn + os.path.splitext(cover.filename)[1])    # 保存名称为isbn + 文件后缀
                resized_filepath = os.path.join(app.config['COVER_UPLOAD_FOLDER'], filename)
                img.save(resized_filepath)
                os.remove(filepath) # 存放好图片后再删去临时图片
            # 插入数据
            cursor.execute('''INSERT into books (title, author, profile, coverpath, isbn, user_id, user_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s )''', (title, author, profile, filename, isbn, user_id, user_name))
            conn.commit()
            # 跳转到对应的书籍页面
            cursor.execute("SELECT * FROM books WHERE isbn = %s", (isbn,))
            book = cursor.fetchone()
            book_id = book['id']
            cursor.close()
            conn.close()
            flash('新增书籍成功')
            return redirect(url_for('book', book_id = book_id))
        cursor.close()
        conn.close()
    return render_template('new_book.html')

# 修改书籍
@app.route('/book/<int:book_id>/edit/', methods = ('GET', 'POST'))
def edit_book(book_id):
    # 查看登录状态，若未登录则跳转到登录页
    if not('username' in session) or not('user_id' in session) :
        return redirect(url_for('login'))
    # 从数据表中取指定书籍的信息
    conn = database_connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    if not book:
        flash('书籍不存在')
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    if not (session['user_id'] == book['user_id']):
        flash('没有编辑该书籍的权限')
        cursor.close()
        conn.close()
        return redirect(url_for('book', book_id = book_id))
    if request.method == 'POST':
        # 从表单中取数据
        title = request.form['title']
        author = request.form['author']
        profile = request.form['profile']
        cover = request.files.get('cover')
        isbn = request.form['isbn']
        if not profile or len(profile) < 1:
            profile = "-"
        # 合法性检查
        cursor.execute("SELECT * FROM books WHERE isbn = %s", (isbn,))
        otherbook = cursor.fetchone()
        if not (isbn == book['isbn']) and otherbook:
            flash('ISBN相同的书籍已存在')
        elif len(title) < 1 or len(title) > 255:
            flash('标题长度为1~255')
        elif len(author) < 1 or len(author) > 255:
            flash('作者长度为1~255')
        elif len(profile) > 2000:
            flash('简介长度不能大于2000')
        elif not (len(isbn) == 13):
            flash('ISBN格式错误（需要13位数字）')
        elif request.content_length > MAX_FILE_SIZE:
            flash('文件太大，无法上传' + ' (限制为' + str(MAX_FILE_SIZE / 1024 / 1024) + 'MB)')
        else:
            filename = book['coverpath']
            # 在服务器更新保存图片文件
            if cover:
                os.remove(os.path.join(app.config['COVER_UPLOAD_FOLDER'], book['coverpath'])) # 删去原图片
                filepath = ''
                filename = secure_filename('temp_' + isbn + os.path.splitext(cover.filename)[1])    # 临时文件存储修改后的图片
                filepath = os.path.join(app.config['COVER_UPLOAD_FOLDER'], filename)
                if not os.path.exists(app.config['COVER_UPLOAD_FOLDER']):   # 不存在对应路径时，生成新路径
                    os.makedirs(app.config['COVER_UPLOAD_FOLDER']) 
                cover.save(filepath)
                # 缩放图片尺寸
                with Image.open(filepath) as img:
                    img = img.resize((TARGET_COVER_WIDTH, TARGET_COVER_HEIGHT))
                    filename = secure_filename(isbn + os.path.splitext(cover.filename)[1])    # 保存名称为isbn + 文件后缀
                    resized_filepath = os.path.join(app.config['COVER_UPLOAD_FOLDER'], filename)
                    img.save(resized_filepath)
                    os.remove(filepath) # 存储好后删去临时图片
            # 修改数据
            cursor.execute('''UPDATE books
                SET title = %s, author = %s, profile = %s, coverpath = %s, isbn = %s 
                WHERE id = %s''', (title, author, profile, filename, isbn, book_id))
            conn.commit()
            # 跳转到对应的书籍页面
            cursor.execute("SELECT * FROM books WHERE isbn = %s", (isbn,))
            book = cursor.fetchone()
            book_id = book['id']
            cursor.close()
            conn.close()
            flash('书籍已更新')
            return redirect(url_for('book', book_id = book_id))
    cursor.close()
    conn.close()
    return render_template('edit_book.html', book = book)

# 删除书籍
@app.route('/delete_book/<int:book_id>/', methods = ('POST',))
def delete_book(book_id):
    # 查看登录状态，若未登录则跳转到登录页
    if not('username' in session) or not('user_id' in session) :
        return redirect(url_for('login'))
    # 从数据表中取指定书籍的信息
    conn = database_connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    if not book:#寻找是否有相关书籍
        flash('书籍不存在')
        cursor.close()
        conn.close()
        return redirect(url_for("index"))
    if not (session['user_id'] == book['user_id']):
        flash('没有删除该书籍的权限')
        cursor.close()
        conn.close()
        return redirect(url_for('book', book_id = book_id))
    #删除封面文件
    os.remove(os.path.join(app.config['COVER_UPLOAD_FOLDER'], book['coverpath'])) # 删去原图片
    #删除数据表中对应的数据
    cursor.execute('''DELETE FROM books WHERE id = %s''', (book['id'],))
    conn.commit()
    cursor.close()
    conn.close()
    flash('书籍已删除')#相关数据删除完 表明书籍已经删除
    return redirect(url_for('index'))

# 书籍信息页
@app.route('/book/<int:book_id>/')
def book(book_id):
    # 取用户名
    username = None 
    user_id = None 
    if 'username' in session:
        username = session['username']
    if 'user_id' in session:
        user_id = session['user_id']
    # 根据book_id取书籍
    conn = database_connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    if not book:    #若没有对应书籍，则跳转到主页 并说明书籍不存在 
        flash("书籍不存在")
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    # 根据book_id取评论
    cursor.execute("SELECT * FROM reviews WHERE book_id = %s ORDER BY created", (book_id,))
    reviews = cursor.fetchall()
    # 根据book_id取平均评分
    cursor.execute("SELECT * FROM reviews WHERE book_id = %s", (book_id,))
    reviews = cursor.fetchall()
    total, average_rating, rating_num, user_review_id = 0, 0, 0, None
    for review in reviews:
        total += review['rating']
        rating_num += 1
        if review['user_id'] == user_id:
            user_review_id = review['id'];
        cursor.execute("SELECT * FROM users WHERE id = %s", (review['user_id'],))
        user = cursor.fetchone()
        review['user_name'] = user['username']
    if not (rating_num == 0):
        average_rating = total / rating_num
    cursor.close()
    conn.close()
    return render_template('book.html',
        username = username, user_id = user_id, book = book, reviews = reviews, average_rating = average_rating, user_review_id = user_review_id)

# 新增评论
@app.route('/book/<int:book_id>/new_review/', methods = ('GET', 'POST'))
def new_review(book_id):
    # 一切操作前先检查登录状态
    # 查看登录状态，若未登录则跳转到登录页
    if not('username' in session):
        return redirect(url_for("login"))
    user_id = session['user_id']
    user_name = session['username']
    # 连接数据库        
    conn = database_connect()
    cursor = conn.cursor(dictionary=True)
    # 检查书籍是否存在
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    if not book:    #如果没有对应书籍，则跳转到主页
        flash("书籍不存在")
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    # 检查该用户是否已有评论
    cursor.execute("SELECT * FROM reviews WHERE user_id = %s AND book_id = %s", (user_id, book_id))
    review = cursor.fetchone()
    if review:  # 如果评论已经存在 限制一人一个评论防止刷恶评
        cursor.close()
        conn.close()
        return redirect(url_for('edit_review', review_id=review['id']))
    if request.method == 'POST':
        # 从表单中取数据
        content = request.form['content']
        rating = int(request.form.get('rating', '0'))
        # 对于评论的合法性检查，（是否有评论内容以及给出评分）
        if not content or len(content) < 1:
            flash("评论内容不能为空")
        elif not rating or rating < 1 or rating > 5:
            flash("需要给出评分")
        else:
            # 插入数据 把评论内容和评分进行上传
            cursor.execute('''INSERT into reviews (content, rating, book_id, user_id, user_name)
                VALUES (%s, %s, %s, %s, %s)''', (content, rating, book_id, user_id, user_name))
            conn.commit()
            #新增评论成功  跳转到对应的书籍页面
            flash("添加评论成功")
            cursor.close()
            conn.close()
            return redirect(url_for('book', book_id = book_id))
    cursor.close()
    conn.close()
    return render_template('new_review.html', book = book)

#删除评论
@app.route('/delete_review/<int:review_id>/', methods=('POST',))
def delete_review(review_id):
    #一切操作执勤啊优先 检查登录状态
    if not ('username' in session):
        return redirect(url_for("login"))
    user_id = session['user_id']  # 获取当前登录用户的 ID
    # 连接数据库
    conn = database_connect()
    cursor = conn.cursor(dictionary=True)
    # 检查评论是否存在并且是否属于当前用户
    cursor.execute("SELECT * FROM reviews WHERE id = %s", (review_id,))
    review = cursor.fetchone()
    if not review:  
        # 如果评论不存在
        flash("评论不存在")
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    if review['user_id'] != user_id:  
        # 如果评论不属于当前用户
        flash("没有删除该评论的权限")
        cursor.close()
        conn.close()
        return redirect(url_for('book', book_id=review['book_id']))
    # 执行删除操作
    cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
    conn.commit()
    # 获取书籍 ID，方便跳转 回到相应书籍的界面
    book_id = review['book_id']
    flash("评论已删除")
    cursor.close()
    conn.close()
    return redirect(url_for('book', book_id=book_id))

#编辑评论
@app.route('/edit_review/<int:review_id>/', methods=('GET', 'POST'))
def edit_review(review_id):
    #一切操作开始之前 检查登录状态
    if not ('username' in session):
        return redirect(url_for("login"))
    user_id = session['user_id']  # 获取当前登录用户的 ID
    # 连接数据库
    conn = database_connect()
    cursor = conn.cursor(dictionary=True)
    # 检查评论是否存在并且是否属于当前用户
    cursor.execute("SELECT * FROM reviews WHERE id = %s", (review_id,))
    review = cursor.fetchone()
    if not review:  
        # 如果评论不存在
        flash("评论不存在")
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    if review['user_id'] != user_id: 
         # 如果评论不属于当前用户
        flash("没有编辑该评论的权限")
        cursor.close()
        conn.close()
        return redirect(url_for('book', book_id=review['book_id']))
    # 提取book（顺便检查书籍是否存在）
    cursor.execute("SELECT * FROM books WHERE id = %s", (review['book_id'],))
    book = cursor.fetchone()
    if not book:
        #如果编辑评论的书籍不存在
        flash("书籍不存在")
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    # 如果是 POST 请求，则 执行编辑逻辑 对于评价内容和评分进行再一次的修改
    if request.method == 'POST':
        content = request.form['content']
        rating = int(request.form.get('rating', '0'))
        # 数据合法性检查 和上述新增评论的要求一致
        if not content or len(content) < 1:
            flash("评论内容不能为空")
        elif not rating or rating < 1 or rating > 5:  # 假设评分范围是 1-5
            flash("需要给出评分")
        else:
            # 更新评论
            cursor.execute('''
                UPDATE reviews
                SET content = %s, rating = %s
                WHERE id = %s
            ''', (content, rating, review_id))
            conn.commit()
            flash("评论已更新")
            cursor.close()
            conn.close()
            return redirect(url_for('book', book_id=review['book_id']))
    cursor.close()
    conn.close()
    return render_template('edit_review.html', review=review, book=book)

# 用户登录
@app.route('/login/', methods = ('GET', 'POST'))
def login():
    #检查是否已经是登录状态 如果是 说明已经登录
    if 'username' in session:
        flash("您已登录")
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = database_connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user or user['password'] != password:
            flash('用户名或密码错误')
        else:
            session['username'] = username
            session['user_id'] = user['id']
            cursor.close()
            conn.close()
            flash('登录成功')
            return redirect(url_for('index'))
        cursor.close()
        conn.close()
    return render_template('login.html')

# 注册
@app.route('/register/', methods = ('GET', 'POST'))
def register():
    if 'username' in session:
        flash("您已登录")
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        question = request.form['securityQuestion']
        answer = request.form['securityAnswer']
        if len(username) < 2 or len(username) > 30:
            flash('用户名长度为2~30')
            return render_template('register.html')
        elif len(password) < 6 or len(password) > 20:
            flash('密码长度为6~20')
            return render_template('register.html')
        elif len(question) < 1 or len(question) > 255:
            flash('密保问题长度为1~255')
        elif len(answer) < 1 or len(answer) > 255:
            flash('密保答案长度为1~255')
            return render_template('register.html')
        conn = database_connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            #对于用户名的重复性进行检查
            flash('该用户名已被注册')
            cursor.close()
            conn.close()
        elif password != request.form['confirmPassword']:
            #进行比较两次输入的密码 如果两次密码不一致进行反馈
            flash('两次输入的密码不一致')
            cursor.close()
            conn.close()
        else:
            cursor.execute('''INSERT into users (username, password, question, answer)
                VALUES (%s, %s, %s, %s)''', (username, password, question, answer))   
             #向users数据表插入数据 创建新的用户
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))  
            #注册的同时实现登录
            user = cursor.fetchone()
            session['username'] = username
            session['user_id'] = user['id']
            cursor.close()
            conn.close()
            flash('注册成功')
            return redirect(url_for('index'))
    return render_template('register.html')

# 注销账号
@app.route('/logout/', methods = ('POST',))
def logout():
    #要保证在登录状态下才可以进行注销账号
    if not ('username' in session):
        flash("暂未登录，无法注销")
        return redirect(url_for('index'))
    session.pop('username', None)
    session.pop('user_id', None)
    flash('注销成功')
    return redirect(url_for('index'))

# 找回密码
@app.route('/forget/', methods =  ('GET', 'POST'))
def forget():
    #要保证在登录状态下才可以进行找回密码
    if 'username' in session:
        flash("您已登录")
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['newPassword']
        answer = request.form['securityAnswer']
        #查看用户是否存在 并进行对密保问题的验证 并根据需要设置新密码并进行判断
        conn = database_connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user:
            flash('该用户不存在')
            cursor.close()
            conn.close()
        elif not (user['answer'] == answer):
            flash('密保问题答案错误')
            cursor.close()
            conn.close()
        elif len(password) < 6 or len(password) > 20:
            flash('密码长度为6~20')
            cursor.close()
            conn.close()
        elif password != request.form['confirmNewPassword']:
            flash('两次输入的密码不一致')
            cursor.close()
            conn.close()
        else:
            cursor.execute('''UPDATE users
                SET password = %s WHERE username = %s''', 
                (password, username))    
            #修改users数据表的数据 更改相应数据库
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))  
            #修改密码的同时进行登录
            user = cursor.fetchone()
            session['username'] = username
            session['user_id'] = user['id']
            cursor.close()
            conn.close()
            flash('密码修改成功')
            return redirect(url_for('index'))
    return render_template('forget.html')

# 根据用户名实时获取密保问题
@app.route('/get_security_question', methods=['GET'])
def get_security_question():
    username = request.args.get('username')
    if not username:
        return jsonify({"security_question": "输入用户名以获取密保问题"})
    else:
        conn = database_connect()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        cursor.close()
        #根据用户名判断是否存在
        if not user:
            return jsonify({"security_question": "该用户不存在"})
        else:
            return jsonify({"security_question": user['question']})

# 个人主页
@app.route('/user/<int:user_id>')
def user(user_id):
    # 取用户名
    self_username = None 
    self_user_id = None 
    if 'username' in session:
        self_username = session['username']
    if 'user_id' in session:
        self_user_id = session['user_id']
    #检查用户是否存在
    conn = database_connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        flash('该用户不存在')
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    # 提取用户发表的评论
    cursor.execute("SELECT * FROM reviews WHERE user_id = %s ORDER BY created", (user_id,))
    reviews = cursor.fetchall()
    for review in reviews:  
        # 每一条评论提取相关书籍和作者名 显示用户在哪本书下进行了相关评论
        cursor.execute("SELECT * FROM books WHERE id = %s", (review['book_id'],))
        book = cursor.fetchone()
        review['book_title'] = book['title']
        review['book_author'] = book['author']
        cursor.execute("SELECT * FROM users WHERE id = %s", (review['user_id'],))
        this_user = cursor.fetchone()
        review['user_name'] = this_user['username']
    return render_template('user.html', user = user, self_username = self_username, self_user_id = self_user_id, reviews = reviews)

# 编辑个人信息
@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    # 查看是否登录 仅在登录状态下可以进行编辑个人信息
    if not ('username' in session and 'user_id' in session):
        return redirect(url_for('login'))
    user_id = session['user_id']
    # 提取用户信息
    conn = database_connect()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    # 传递提交表单 对于用户名 个性签名 头像的再次编辑
    if request.method == 'POST':
        username = request.form['username']
        bio = request.form['bio']
        profile = request.files.get('profile')
        if len(username) < 2 or len(username) > 30:
            flash('用户名长度为2~30')
            cursor.close()
            conn.close()
            return render_template('edit_user.html', user = user)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        otheruser = cursor.fetchone()
        if not username == session['username'] and otheruser:
            flash('该用户名已存在')
        elif len(bio) < 1 or len(bio) > 80:
            flash('个性签名长度为1~80')
        elif request.content_length > MAX_FILE_SIZE:
            flash('文件太大，无法上传' + ' (限制为' + str(MAX_FILE_SIZE / 1024 / 1024) + 'MB)')
        else:
            filename = user['profilepath']   
             # 默认的头像图片
            # 如果有上传新的头像，在服务器更新保存图片文件
            if profile:
                filepath = ''
                filename = secure_filename('temp_' + str(user_id) + os.path.splitext(profile.filename)[1])    # 临时文件
                filepath = os.path.join(app.config['USERPROFILE_UPLOAD_FOLDER'], filename)
                if not os.path.exists(app.config['USERPROFILE_UPLOAD_FOLDER']):   # 不存在对应路径时，生成路径
                    os.makedirs(app.config['USERPROFILE_UPLOAD_FOLDER']) 
                profile.save(filepath)
                # 进行缩放图片尺寸 先存在临时图片
                with Image.open(filepath) as img:
                    img = img.resize((TARGET_USERPROFILE_WIDTH, TARGET_USERPROFILE_HEIGHT))
                    filename = secure_filename(str(user_id) + os.path.splitext(profile.filename)[1])   
                     # 保存名称为user_id + 文件后缀 代表是谁的头像
                    resized_filepath = os.path.join(app.config['USERPROFILE_UPLOAD_FOLDER'], filename)
                    img.save(resized_filepath)
                    os.remove(filepath) 
                    # 删去临时图片
            # 在数据库修改数据
            cursor.execute('''UPDATE users
                SET username = %s, bio = %s, profilepath = %s 
                WHERE id = %s''', (username, bio, filename, user_id))
            conn.commit()
            # 跳转到对应的个人主页
            cursor.close()
            conn.close()
            session['username'] = username
            flash('个人信息修改成功')
            return redirect(url_for('user', user_id = user_id))
    cursor.close()
    conn.close()
    return render_template('edit_user.html', user = user)



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    # 创建数据表
    create_table()
    app.run(debug=True)