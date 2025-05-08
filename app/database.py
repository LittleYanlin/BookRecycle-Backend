from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from datetime import timedelta
app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # 上传文件存储路径
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 限制上传文件大小为 5 MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # 允许的文件类型
app.config['JWT_SECRET_KEY'] = 'fjwoeifjwkjdkwxlkwkdkkHUKJDCKWlkhncjerjwkc'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
db = SQLAlchemy(app)
jwt = JWTManager(app)
class Stu(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    place = db.Column(db.Integer, nullable=True)
    score = db.Column(db.Integer,default=100)
    money = db.Column(db.Float,default=0)
    phone = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    shoukuan = db.Column(db.String, nullable=False)
class Booker(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    place = db.Column(db.Integer, nullable=True)
    money = db.Column(db.Float,default=0)
    phone = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
class Book_Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    place = db.Column(db.Integer, nullable=False)
    print_edition = db.Column(db.String, nullable=True)
    publisher = db.Column(db.String, nullable=True)
    img_url = db.Column(db.String, nullable=True)
    uploader = db.Column(db.String,nullable=False)
    available = db.Column(db.Boolean, default=True)
    time = db.Column(db.String)
class Book_Recycle(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uploader = db.Column(db.String,nullable=False)
    place = db.Column(db.Integer,nullable=False)
    img_url = db.Column(db.String,nullable=True)
    available = db.Column(db.Boolean, default=True)
    booker = db.Column(db.String,nullable=True)
    isend= db.Column(db.Boolean, default=False)
    kg_upload = db.Column(db.Float,default=0)
    kg_real = db.Column(db.Float,default=0)
    money_uploader = db.Column(db.Float,default=0)
    money_booker = db.Column(db.Float,default=0)
    time = db.Column(db.String)
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poster = db.Column(db.String,nullable=False)
    receiver = db.Column(db.String,nullable=False)
    data = db.Column(db.String)
    time = db.Column(db.String)
class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    money_per_kg=db.Column(db.Float,default=10)
    rate=db.Column(db.Float,default=0.2)
    score=db.Column(db.Float,default=60)
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    user_manage = db.Column(db.Boolean, default=False)
    score_manage = db.Column(db.Boolean, default=False)
    content_manage = db.Column(db.Boolean, default=False)
    super_admin= db.Column(db.Boolean, default=False)
class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String, nullable=False)
    uploader = db.Column(db.String, nullable=False)
    time = db.Column(db.String)
class Reason(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reason = db.Column(db.String)
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    available = db.Column(db.Boolean, default=True)
    admin=db.Column(db.String)
    report_user=db.Column(db.String)
    reported_user=db.Column(db.String)
    message=db.Column(db.String)
    time=db.Column(db.String)
    score=db.Column(db.Float)
    data=db.Column(db.String)