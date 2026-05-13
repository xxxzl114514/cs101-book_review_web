# 济计好书网

基于 Flask 的书籍评价与分享 Web 应用。

## 功能

- 用户注册、登录、找回密码
- 浏览书籍、搜索书籍、随机刷新推荐
- 新增/编辑/删除书籍
- 撰写/编辑/删除书评（1-5 分评分制）
- 个人主页，编辑用户名、个性签名、头像
- 每人每书限评一次，防止恶意刷分

## 技术栈

- **后端**: Python Flask
- **数据库**: MySQL（mysql-connector-python）
- **前端**: HTML + CSS + JavaScript + jQuery
- **图片处理**: Pillow

## 本地运行

1. 安装依赖

```bash
pip install flask mysql-connector-python pillow werkzeug
```

2. 确保本地 MySQL 已运行，创建数据库：

```sql
CREATE DATABASE bookreview;
```

3. 修改 `bookreview-codes/database.py` 中的数据库连接配置（用户名、密码）。

4. 启动应用

```bash
cd bookreview-codes
python bookreview.py
```

5. 打开浏览器访问 `http://127.0.0.1:5000`

## 项目结构

```
bookreview-codes/
├── bookreview.py          # 主应用（路由与业务逻辑）
├── database.py            # 数据库连接与建表
├── static/
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript 文件
│   ├── covers/            # 书籍封面图片
│   ├── userprofiles/      # 用户头像
│   └── images/            # 背景图等资源
├── templates/             # Jinja2 模板
│   ├── index.html         # 主页
│   ├── login.html         # 登录
│   ├── register.html      # 注册
│   ├── forget.html        # 找回密码
│   ├── book.html          # 书籍详情
│   ├── new_book.html      # 新增书籍
│   ├── edit_book.html     # 编辑书籍
│   ├── new_review.html    # 撰写书评
│   ├── edit_review.html   # 编辑书评
│   ├── user.html          # 个人主页
│   ├── edit_user.html     # 编辑个人信息
│   └── 404.html           # 404 页面
└── templates/             # Jinja2 模板
```
