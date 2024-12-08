from flask import Flask, render_template , url_for ,request,redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
account=""

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    Account = db.Column(db.String(100),nullable=False)
    Password = db.Column(db.String(100),nullable=False)

    def __repr__(self):
        return 'User'+ str(self.id)

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    posterAcc = db.Column(db.String(100),nullable=False)
    title = db.Column(db.String(100),nullable=False)
    intro = db.Column(db.Text,nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Post'+ str(self.id)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    global account
    account=''
    all_posts=Post.query.order_by(Post.id).all()
    return render_template("home.html",posts=all_posts)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        account = request.form['Account']
        password = request.form['Password']
        
        # 验证输入不为空
        if not account or not password:
            flash('账号和密码不能为空')
            return redirect('/register')
        
        # 检查账号是否已存在
        existing_user = User.query.filter_by(Account=account).first()
        if existing_user:
            flash('该账号已存在')
            return redirect('/register')
        
        # 创建新用户，使用密码哈希
        new_user = User(Account=account, Password=password)
        
        try:
            # 添加并提交新用户
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功')
            return redirect('/')
        except Exception as e:
            # 处理可能的数据库错误
            db.session.rollback()
            flash('注册失败，请重试')
            return redirect('/register')
    
    # GET 请求
    return render_template("register.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        global account
        account = request.form['Account']
        password = request.form['Password']

        # 验证输入不为空
        if not account or not password:
            flash('账号和密码不能为空')
            return redirect('/login')
        
        # 检查账号是否正確
        existing_user = User.query.filter_by(Account=account).first()
        if existing_user == None:
            return redirect('/login')
        else:
            check_password = (password == User.query.filter_by(Account=account).first().Password)
            if not check_password:
                return redirect('/')
            else:
                all_posts=Post.query.filter_by(posterAcc=account).order_by(Post.date_posted).all()
                return render_template("index.html",posts = all_posts,poster=account)
    else:
        return render_template("login.html")

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method=='POST':
        title=request.form['title']
        intro=request.form['intro']
        poster=account
        new_post=Post(title=title,intro=intro,posterAcc=poster)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/index')
    else:    
        all_posts=Post.query.filter_by(posterAcc=account).order_by(Post.date_posted).all()
        return render_template("index.html",posts = all_posts,poster=account)

@app.route('/post', methods=['GET', 'POST'])
def post():
    return render_template("post.html")

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    
    post = Post.query.get_or_404(id)
    
    if request.method == 'POST':
        post.title=request.form['title']
        post.intro=request.form['intro']
        post.poster=account
        db.session.commit()
        all_posts=Post.query.filter_by(posterAcc=account).order_by(Post.date_posted).all()
        return render_template("index.html",posts = all_posts,poster=account)
    else:
        return render_template('edit.html', post=post)

@app.route('/posts/delete/<int:id>')
def delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    all_posts=Post.query.filter_by(posterAcc=account).order_by(Post.date_posted).all()
    return render_template("index.html",posts = all_posts,poster=account)

if __name__=='__main__':
    app.run()
