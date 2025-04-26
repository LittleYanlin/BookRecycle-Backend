'''
Author: LittleYanlin
Date: 2025-4-26
Description: 旧书回收系统后端
Version: 1.0
'''
from flask import Flask,request,url_for, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
import time
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import uuid
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity , get_jwt
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
@app.cli.command()
def create():
    db.create_all()
    setting=Setting(
        money_per_kg=10,
        rate=0.2,
        score=10
    )
    admin=Admin(
        username="zhouyanlin",
        password="abc123456",
        user_manage=True,
        score_manage=True,
        content_manage=True,
        super_admin=True
    )
    db.session.add(admin)
    db.session.add(setting)
    db.session.commit()
def check_login(username_input, password):
    user = Stu.query.filter_by(username=username_input).first()
    setting=Setting.query.first().score
    if not user:
        return False
    if int(user.score)<int(setting):
        return False
    return user.password == password
def check_score_ava(score):
    setting=Setting.query.first().score
    return score>=setting
def check_booker_login(username,password):
    user=Booker.query.filter_by(username=username).first()
    if not user:
        return False
    return user.password==password
def check_admin_login(username,password):
    user=Admin.query.filter_by(username=username).first()
    if not user:
        return False
    return user.password==password
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
def manage_data(message):
    temp = []
    for t in message:
        poster = t.poster
        flag = False
        j = 0
        for i in range(len(temp)):
            if poster == temp[i][0]:
                flag = True
                j = i
                break
        if not flag:
            temp.append([poster, [], []])
            temp[len(temp)-1][1].append(t.data)
            temp[len(temp)-1][2].append(t.time)
        else:
            if(len(temp[j][1])>=3):
                temp[j][1].pop(0)
                temp[j][2].pop(0)
            temp[j][1].append(t.data)
            temp[j][2].append(t.time)
    return temp
@app.route('/')
def index():
    return "后端启动成功！"
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  # 必须提供 refresh_token
def refresh():
    current_user = get_jwt_identity()
    role=get_jwt()["role"]
    new_access_token = create_access_token(identity=str(current_user),additional_claims={"role":role})
    return{
        "status":1,
        "access_token":new_access_token
    }
@app.route('/login', methods=['POST'])
def login():
    try:
        role = request.form.get("role")
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return {
                "status": 0,
                "message": "用户名或密码不能为空！"
            }
        if role=="1":
            if check_login(username, password):
                access_token = create_access_token(identity=str(username),additional_claims={"role":role})
                refresh_token = create_refresh_token(identity=str(username),additional_claims={"role":role})
                return {
                    "status": 1,
                    "message": "登录成功！",
                    "access_token":access_token,
                    "refresh_token":refresh_token
                }
            else:
                return {
                    "status": 0,
                    "message": "登录失败，请检查你的账号密码"
                }
        elif role=="2":
            if check_booker_login(username,password):
                access_token = create_access_token(identity=username,additional_claims={"role":role})
                refresh_token = create_refresh_token(identity=username,additional_claims={"role":role})
                return {
                    "status": 1,
                    "message": "登录成功！",
                    "access_token":access_token,
                    "refresh_token":refresh_token
                }
            else:
                return {
                    "status": 0,
                    "message": "登录失败，请检查你的账号密码"
                }
        else:
            if check_admin_login(username,password):
                access_token = create_access_token(identity=username,additional_claims={"role":role})
                refresh_token = create_refresh_token(identity=username,additional_claims={"role":role})
                return {
                    "status": 1,
                    "message": "登录成功！",
                    "access_token":access_token,
                    "refresh_token":refresh_token
                }
            else:
                return {
                    "status": 0,
                    "message": "登录失败，请检查你的账号密码"
                }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/check_first_login',methods=['POST'])
def first_login():
    try:
        role = request.form.get("role")
        if role!="1":
            return{
                "status":1,
                "result":False
            }
        username=request.form.get("username")
        password=request.form.get("password")
        user=Stu.query.filter_by(username=username).first()
        if not user and username[-6:]==password[4:] and password[:4]=='zjut':
            return{
                "status":1,
                "result":True
            }
        return{
            "status":1,
            "result":False
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/get_uploaded_books', methods=['POST'])#旧书再利用模块
@jwt_required()
def get_books():
    try:
        username=get_jwt_identity()
        user=Stu.query.filter_by(username=username).first()
        action=request.form.get("action")
        if(get_jwt()["role"]=="3"):
            books=Book_Upload.query.all()
        else:
            if action=='all':
                books = Book_Upload.query.filter(and_(Book_Upload.place==user.place,Book_Upload.available,Book_Upload.uploader!=username)).all()
            else:
                books=Book_Upload.query.filter_by(uploader=username).all()
        result = [{
            "name": book.name,
            "place": book.place,
            "print_edition": book.print_edition,
            "publisher": book.publisher,
            "img_url": book.img_url,
            "uploader": book.uploader,
            "available": book.available,
            "id":book.id,
            "time":book.time
        } for book in reversed(books)]
        return {
            "status": 1,
            "result": result
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/get_user_upload_books', methods=['POST'])#显示旧书回收模块
@jwt_required()
def get_other_books():
    try:
        username=get_jwt_identity()
        action=request.form.get("action")
        if action=='all':
            user=Booker.query.filter_by(username=username).first()
            books = Book_Recycle.query.filter(and_(Book_Recycle.place==user.place,Book_Recycle.available)).all()
            result = [{
                "uploader":book.uploader,
                "img_url":book.img_url,
                "kg_upload":book.kg_upload,
                "id":book.id,
                "time":book.time,
                "available":book.available,
                "idend":book.isend
            } for book in reversed(books)]
            return {
                "status": 1,
                "result": result
            }
        elif action=='stu_check':
            books = Book_Recycle.query.filter(Book_Recycle.uploader==username).all()
            result = [{
                "uploader":book.uploader,
                "img_url":book.img_url,
                "kg_upload":book.kg_upload,
                "kg_real":book.kg_real,
                "available":book.available,
                "money_uploader":book.money_uploader,
                "money_booker":book.money_booker,
                "isend":book.isend,
                "id":book.id,
                "booker":book.booker,
                "time":book.time,
            } for book in reversed(books)]
            return {
                "status": 1,
                "result": result
            }
        elif action=='booker_check':
            books = Book_Recycle.query.filter(Book_Recycle.booker==username).all()
            result = [{
                "uploader":book.uploader,
                "img_url":book.img_url,
                "kg_upload":book.kg_upload,
                "kg_real":book.kg_real,
                "available":book.available,
                "money_uploader":book.money_uploader,
                "money_booker":book.money_booker,
                "isend":book.isend,
                "id":book.id,
                "booker":book.booker,
                "time":book.time,
            } for book in reversed(books)]
            return {
                "status": 1,
                "result": result
            }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/upload_book', methods=['POST'])
@jwt_required()
def upload():
    try:
        user = get_jwt_identity()
        if get_jwt()["role"]!="1":
            return {
                "status": 0,
                "message": "未授权"
            }
        if not request.form.get("img_url"):
            return {
                "status": 0,
                "message": "图片链接不能为空"
            }
        kg=request.form.get("kg_upload")
        if not kg:
            return {
                "status": 0,
                "message": "重量不能为空"
            }
        user_obj = Stu.query.filter_by(username=user).first()
        if not check_score_ava(user_obj.score):
            return {
                "status": 0,
                "message": "你已经低于最低信誉分，按照规定限制功能！"
            }
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        new_book = Book_Recycle(
            place=user_obj.place,
            img_url=request.form.get("img_url"),
            uploader=user,
            available=True,
            kg_upload=float(kg),
            isend=False,
            time = formatted_time
        )
        db.session.add(new_book)
        db.session.commit()
        set_data=Setting.query.first()
        print(request.form.get("kg_upload"))
        money=float(set_data.money_per_kg)*float(request.form.get("kg_upload"))*(1-float(set_data.rate))
        return {
            "status": 1,
            "message": "添加成功！等待收书员收单",
            "money":money
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/shoushu',methods=['POST'])
@jwt_required()
def shoushu():
    try:
        user = get_jwt_identity()
        data=Book_Recycle.query.filter_by(id=request.form.get("id")).first()
        if data.booker!=user or data.isend or get_jwt()["role"]!="2":
            return {
                "status": 0,
                "message": "未授权"
            }
        if not request.form.get("img_url"):
            return {
                "status": 0,
                "message": "图片链接不能为空"
            }
        if not request.form.get("kg_real"):
            return {
                "status": 0,
                "message": "重量不能为空"
            }
        userData=Stu.query.filter_by(username=data.uploader).first()
        bookerData=Booker.query.filter_by(username=user).first()
        setting=Setting.query.first()
        data.img_url=request.form.get("img_url")
        data.isend=True
        data.kg_real=request.form.get("kg_real")
        total_money=round(setting.money_per_kg*float(request.form.get("kg_real")),2)
        booker_money=round(total_money*setting.rate,2)
        bookerData.money+=booker_money
        userData.money+=(total_money-booker_money)
        data.money_uploader=total_money-booker_money
        data.money_booker=booker_money
        db.session.commit()
        return{
            "status":1,
            "message":"上传成功并已获得奖励",
            "money":bookerData.money
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/get_order",methods=['POST'])
@jwt_required()
def get_order():
    try:
        user = get_jwt_identity()
        userData=Booker.query.filter_by(username=user).first()
        data=Book_Recycle.query.filter_by(id=request.form.get("id")).first()
        if not data:
            return {
                "status": 0,
                "message": "未查询到这个订单的信息，请刷新页面"
            }
        if not userData or get_jwt()["role"]!="2":
            return {
                "status": 0,
                "message": "未授权"
            }
        if data.available:
            data.available=False
            data.booker=user
            db.session.commit()
            return{
                "status":1,
                "message":"收书成功！请尽快前往收书并上传信息！"
            }
        else:
            return{
                "status":0,
                "message":"该书已被其他收书员负责！"
            }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/get_order_detail",methods=['POST'])
@jwt_required()
def get_order_detail():
    try:
        user = get_jwt_identity()
        data=Book_Recycle.query.filter_by(id=request.form.get("id")).first()
        uploader=Stu.query.filter_by(username=data.uploader).first()
        if get_jwt()["role"]!="2" or data.booker!=user:
            return {
                "status": 0,
                "message": "未授权"
            }
        if not data:
            return {
                "status": 0,
                "message": "未查询到这个订单的信息，请刷新页面"
            }
        return{
            "status":1,
            "result":{
                "phone":uploader.phone,
                "address":uploader.address
            }
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/reg",methods=['POST'])
def reg():
    try:
        reg_role=request.form.get("role")
        if reg_role=="1":
            new_user=Stu(
                username=request.form.get("username"),
                password=request.form.get("password"),
                place=request.form.get("place"),
                phone=request.form.get("phone"),
                shoukuan=request.form.get("shoukuan"),
                address=request.form.get("address"),
                score=100,
                money=0
            )
            if not new_user.address or not new_user.username or not new_user.password or not new_user.place or not new_user.phone or not new_user.shoukuan or not new_user.address:
                return{
                "status":0,
                "message":"请检查你的输入内容"
            }
            old=Stu.query.filter_by(username=request.form.get("username")).first()
            if old:
                return{
                "status":0,
                "message":"该学号已经被注册过！"
            }
            db.session.add(new_user)
            db.session.commit()
            access_token = create_access_token(identity=request.form.get("username"),additional_claims={"role":"1"})
            refresh_token = create_refresh_token(identity=request.form.get("username"),additional_claims={"role":"1"})
            return{
                "status":1,
                "message":"注册成功！请前往登录",
                "access_token":access_token,
                "refresh_token":refresh_token
            }
        elif reg_role=="2":
            new_user=Booker(
                username=request.form.get("username"),
                password=request.form.get("password"),
                place=request.form.get("place"),
                phone=request.form.get("phone"),
                name=request.form.get("name"),
                money=0
            )
            if not new_user.username or not new_user.password or not new_user.place or not new_user.phone or not new_user.name:
                return{
                "status":0,
                "message":"请检查你的输入内容"
            }
            old=Booker.query.filter_by(username=request.form.get("username")).first()
            if old:
                return{
                "status":0,
                "message":"该学号已经被注册过！"
            }
            db.session.add(new_user)
            db.session.commit()
            return{
                "status":1,
                "message":"注册成功！请前往登录"
            }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/upload_book_hub",methods=['POST'])
@jwt_required()
def upload_hub():
    try:
        user = get_jwt_identity()
        if get_jwt()["role"]!="1":
            return {
                "status": 0,
                "message": "未授权"
            }
        userData=Stu.query.filter_by(username=user).first()
        if not check_score_ava(userData.score):
            return {
                "status": 0,
                "message": "你已经低于最低信誉分，按照规定限制功能！"
            }
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        data=Book_Upload(
            name=request.form.get("name"),
            place=userData.place,
            print_edition=request.form.get("print_edition"),
            publisher=request.form.get("publisher"),
            img_url=request.form.get("img_url"),
            available=True,
            time=formatted_time,
            uploader=user
        )
        if not data.name or not data.print_edition or not data.publisher or not data.img_url:
                return{
                "status":0,
                "message":"请检查你的输入内容"
            }
        db.session.add(data)
        db.session.commit()
        return{
            "status":1,
            "message":"上传成功！"
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/book_end",methods=['POST'])
@jwt_required()
def book_end():
    try:
        user = get_jwt_identity()
        data=Book_Upload.query.filter_by(id=request.form.get("id")).first()
        if not data:
            return{
                "status":0,
                "message":"未找到这笔订单，请刷新页面"
            }
        if get_jwt()["role"]!="1" or not user==data.uploader:
            return {
                "status": 0,
                "message": "未授权"
            }
        data.available=False
        db.session.commit()
        return{
            "status":1,
            "message":"交易完成！"
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/admin/user/stu",methods=['POST'])
@jwt_required()
def manage_user():
    try:
        user = get_jwt_identity()
        adminData=Admin.query.filter_by(username=user).first()
        if get_jwt()["role"]!="3" or not adminData.user_manage or not adminData:
            return {
                "status": 0,
                "message": "未授权"
            }
        stuData=Stu.query.all()
        result=[{
            "username":data.username,
            "score":data.score,
            "money":str(round(data.money,2)),
            "phone":data.phone,
            "id":data.id
        }for data in stuData]
        return{
            "status":1,
            "data":result
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/admin/user/stu_manage",methods=['POST'])
@jwt_required()
def stu_manage():
    try:
        user = get_jwt_identity()
        adminData=Admin.query.filter_by(username=user).first()
        if get_jwt()["role"]!="3" or not adminData.user_manage or not adminData:
            return {
                "status": 0,
                "message": "未授权"
            }
        if not request.form.get("score") or not request.form.get("money"):
            return {
                "status": 0,
                "message": "请检查你输入的内容"
            }
        userData=Stu.query.filter_by(id=request.form.get("id")).first()
        if(request.form.get("new_pass")!=''):
            userData.password=request.form.get("new_pass")
        userData.score=request.form.get("score")
        userData.money=request.form.get("money")
        db.session.commit()
        return{
            "status":1,
            "message":"用户数据更新成功！"
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/manage/1",methods=['POST'])
@jwt_required()
def user_manage():
    try:
        user = get_jwt_identity()
        new_pass=request.form.get("new_pass")
        action=request.form.get("action")
        if get_jwt()["role"]!="1":
            return {
                "status": 0,
                "message": "未授权"
            }
        userData=Stu.query.filter_by(username=user).first()
        if action=='check':
            return{
                "status":1,
                "data":{
                    "place":userData.place,
                    "phone":userData.phone,
                    "address":userData.address,
                    "shoukuan":userData.shoukuan,
                    "score":userData.score,
                    "money":str(round(userData.money,2))
                }
            }
        if not request.form.get("place") or not request.form.get("phone") or not request.form.get("address") or not request.form.get("shoukuan"):
            return {
                "status": 0,
                "message": "请检查你输入的内容"
            }
        if new_pass!='':
            userData.password=new_pass
        userData.place=request.form.get("place")
        userData.phone=request.form.get("phone")
        userData.address=request.form.get("address")
        userData.shoukuan=request.form.get("shoukuan")
        db.session.commit()
        return{
            "status":1,
            "message":"用户数据更新成功！"
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/manage/2",methods=['POST'])
@jwt_required()
def booker_manage():
    try:
        user = get_jwt_identity()
        new_pass=request.form.get("new_pass")
        action=request.form.get("action")
        if get_jwt()["role"]!="2":
            return {
                "status": 0,
                "message": "未授权"
            }
        userData=Booker.query.filter_by(username=user).first()
        if action=='check':
            return{
                "status":1,
                "data":{
                    "place":userData.place,
                    "phone":userData.phone,
                    "money":str(round(userData.money,2)),
                    "name":userData.name
                }
            }
        if not request.form.get("place") or not request.form.get("phone"):
            return {
                "status": 0,
                "message": "请检查你输入的内容"
            }
        if new_pass!='':
            userData.password=new_pass
        userData.place=request.form.get("place")
        userData.phone=request.form.get("phone")
        db.session.commit()
        return{
            "status":1,
            "message":"用户数据更新成功！"
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/manage/3",methods=['POST'])
@jwt_required()
def admin_manage():
    try:
        user = get_jwt_identity()
        new_pass=request.form.get("new_pass")
        action=request.form.get("action")
        if get_jwt()["role"]!="3":
            return {
                "status": 0,
                "message": "未授权"
            }
        userData=Admin.query.filter_by(username=user).first()
        if action=='check':
            return{
                "status":1,
                "data":{
                    "user_manage":userData.user_manage,
                    "score_manage":userData.score_manage,
                    "content_manage":userData.content_manage,
                    "super_admin":userData.super_admin
                }
            }
        if not new_pass:
            return {
                "status": 0,
                "message": "请检查你输入的内容"
            }
        if new_pass!='':
            userData.password=new_pass
        db.session.commit()
        return{
            "status":1,
            "message":"用户数据更新成功！"
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/chat/get/all",methods=['POST'])
@jwt_required()
def get_data():
    try:
        user = get_jwt_identity()
        if get_jwt()["role"]!="1":
                return {
                    "status": 0,
                    "message": "未授权"
                }
        chatData=Chat.query.filter(Chat.receiver==user).all()
        newData=manage_data(chatData)
        result=[{
                "poster":data[0],
                "data":data[1],
                "time":data[2]
            }for data in reversed(newData)]
        return{
                "status":1,
                "data":result
            }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/chat/get/detail",methods=['POST'])
@jwt_required()
def get_data_detail():
    try:
        request_user=request.form.get("req_user")
        user = get_jwt_identity()
        if get_jwt()["role"]!="1":
                return {
                    "status": 0,
                    "message": "未授权"
                }
        chatData=Chat.query.filter(and_(or_(Chat.receiver==user,Chat.poster==user),or_(Chat.receiver==request_user,Chat.poster==request_user))).all()
        result=[{
                "poster":data.poster,
                "receiver":data.receiver,
                "data":data.data,
                "time":data.time
            }for data in reversed(chatData)]
        return{
                "status":1,
                "data":result
            }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/chat/post",methods=['POST'])
@jwt_required()
def post_data():
    try:
        request_user=request.form.get("req_user")
        user = get_jwt_identity()
        if get_jwt()["role"]!="1":
                return {
                    "status": 0,
                    "message": "未授权"
                }
        if not request.form.get("receiver") or not request.form.get("data"):
            return {
                "status": 0,
                "message": "请检查你输入的内容"
            }
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        new_data=Chat(
                poster=user,
                receiver=request.form.get("receiver"),
                data=request.form.get("data"),
                time=formatted_time
            )
        db.session.add(new_data)
        db.session.commit()
        return{
                "status":1,
                "message":"发送成功！"
            }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route("/upload_img",methods=['POST'])
@jwt_required()
def upload_img():
    try:
        user = get_jwt_identity()
        role = get_jwt()["role"]
        if 'file' not in request.files:
            return{
                "status":0,
                "message":"文件不能为空！"
            }
        file = request.files['file']
        if file.filename == '':
            return{
                "status":0,
                "message":"文件不能为空！"
            }
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_extension = os.path.splitext(filename)[1]
            unique_filename = str(int(time.time())) + "_" + str(uuid.uuid4()) + file_extension
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            file_url = url_for('uploaded_file', filename=unique_filename)
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            data = Img(
                path=filename,
                uploader=user,
                time=formatted_time
            )
            db.session.add(data)
            db.session.commit()
            return{
                "status":1,
                "message":"上传成功！",
                "url":file_url
            }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
@app.route('/admin/score',methods=['POST'])
@jwt_required()
def check_score():
    try:
        user = get_jwt_identity()
        adminData=Admin.query.filter_by(username=user).first()
        if not adminData.score_manage or get_jwt()["role"]!="3":
            return {
                "status": 0,
                "message": "未授权"
            }
        stuData=Report.query.all()
        result=[{
            "report_user":data.report_user,
            "reported_user":data.reported_user,
            "message":data.message,
            "time":data.time,
            "id":data.id,
            "data":data.data,
            "available":data.available,
            "score":data.score
        }for data in stuData]
        return{
            "status":1,
            "data":result
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/admin/score_manage',methods=['POST'])
@jwt_required()
def score_manage():
    try:
        user = get_jwt_identity()
        adminData=Admin.query.filter_by(username=user).first()
        if not adminData.score_manage or get_jwt()["role"]!="3":
            return {
                "status": 0,
                "message": "未授权"
            }
        userData=Stu.query.filter_by(username=request.form.get("stu_username")).first()
        userData.score-=float(request.form.get("score"))
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        reason=Reason.query.filter_by(id=request.form.get("reason")).first().reason
        report=Report.query.filter_by(id=request.form.get("id")).first()
        report.admin=user
        report.score=float(request.form.get("score"))
        report.available=False
        message=Chat(
            poster="管理员",
            receiver=request.form.get("stu_username"),
            data= "亲爱的同学，由于"+reason+"原因，你已被扣除"+str(request.form.get("score"))+"分信誉分，请注意自己的行为！分数过低会限制功能！",
            time=formatted_time
        )
        db.session.add(message)
        db.session.commit()
        return {
            "status": 1,
            "message":"扣分成功！"
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/admin/reason', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def manage_reason():
    try:
        user = get_jwt_identity()
        adminData = Admin.query.filter_by(username=user).first()
        if not adminData.score_manage or get_jwt()["role"]!="3":
            return {"status": 0, "message": "未授权"}
        if request.method == 'GET':
            reasons = Reason.query.all()
            result = [{"id": r.id, "reason": r.reason} for r in reasons]
            return {"status": 1, "data": result}
        if request.method == 'POST':
            reason = request.form.get("reason")
            new_reason = Reason(reason=reason)
            db.session.add(new_reason)
            db.session.commit()
            return {"status": 1, "message": "理由添加成功"}

        if request.method == 'DELETE':
            reason_id = request.headers.get("id")
            reason = Reason.query.filter_by(id=reason_id).first()
            db.session.delete(reason)
            db.session.commit()
            return {"status": 1, "message": "理由删除成功"}

    except Exception as e:
        return {"status": 0, "message": str(e)}
@app.route('/admin/score_cancel',methods=['POST'])
@jwt_required()
def score_cancel():
    try:
        user = get_jwt_identity()
        adminData=Admin.query.filter_by(username=user).first()
        if not adminData.score_manage or get_jwt()["role"]!="3":
            return {
                "status": 0,
                "message": "未授权"
            }
        log=Report.query.filter_by(id=request.form.get("id")).first()
        userData=Stu.query.filter_by(username=log.reported_user).first()
        userData.score+=log.score
        log.available=True
        time_log=log.time
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        message=Chat(
            poster="管理员",
            receiver=log.reported_user,
            data= "亲爱的同学，在"+time_log+"扣除的信誉分已经返还到你的账号！",
            time=formatted_time
        )
        db.session.add(message)
        db.session.commit()
        return{
            "status":1,
            "message":"删除成功！"
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/admin/book_manage',methods=['POST','GET','DELETE'])
@jwt_required()
def book_manage():
    try:
        user = get_jwt_identity()
        adminData=Admin.query.filter_by(username=user).first()
        if get_jwt()["role"]!="3":
            return {
                "status": 0,
                "message": "未授权"
            }
        if request.method=='POST':
            if not adminData.content_manage:
                return {
                    "status": 0,
                    "message": "未授权"
                }
            bookData=Book_Upload.query.filter_by(id=request.form.get("id")).first()
            bookData.name=request.form.get("name")
            bookData.print_edition=request.form.get("print_edition")
            bookData.place=request.form.get("place")
            bookData.publisher=request.form.get("publisher")
            bookData.img_url=request.form.get("img_url")
            bookData.available=request.form.get("available")
            db.session.commit()
            return{
                "status":1,
                "message":"修改成功！"
            }
        if request.method=='GET':
            id=request.headers.get('id')
            if not id:
                books=Book_Upload.query.all()
                result=[{
                    "id":book.id,
                    "name":book.name,
                    "place":book.place,
                    "print_edition":book.print_edition,
                    "publisher":book.publisher,
                    "img_url":book.img_url,
                    "uploader":book.uploader,
                    "available":book.available,
                    "time":book.time
                }for book in books]
                return{
                    "status":1,
                    "result":result
                }
            else:
                book=Book_Upload.query.filter_by(id=id).first()
                result={
                    "uploader":book.uploader,
                    "img_url":book.img_url,
                    "id":book.id,
                    "time":book.time,
                }
            return{
                "status":1,
                "result":result
            }
        if request.method=='DELETE':
            if not adminData.content_manage:
                return {
                    "status": 0,
                    "message": "未授权"
                }
            id=request.headers.get("id")
            book=Book_Upload.query.filter_by(id=id).first()
            available=book.available
            if available:
                book.available=False
                db.session.commit()
                return{
                    "status":1,
                    "message":"封禁成功！"
                }
            book.available=True
            db.session.commit()
            return{
                "status":1,
                "message":"解封成功！"
            }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/manage_book')
@jwt_required()
def book_manage_user():
    try:
        user = get_jwt_identity()
        bookData=Book_Upload.query.filter_by(id=request.form.get("id")).first()
        if not bookData.uploader==user or get_jwt()["role"]!="1":
            return {
                "status": 0,
                "message": "未授权"
            }
        bookData.name=request.form.get("name")
        bookData.print_edition=request.form.get("print_edition")
        bookData.place=request.form.get("place")
        bookData.publisher=request.form.get("publisher")
        bookData.img_url=request.form.get("img_url")
        bookData.available=request.form.get("available")
        db.session.commit()
        return{
            "status":1,
            "message":"修改成功！"
        }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/report',methods=['POST','DELETE','GET'])
@jwt_required()
def report():
    try:
        user = get_jwt_identity()
        if get_jwt()["role"]!="1":
                return {
                    "status": 0,
                    "message": "未授权"
                }
        if request.method=='POST':
            now = datetime.now()
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            data=Report(
                available=True,
                report_user=user,
                reported_user=request.form.get("reported_user"),
                message=request.form.get("message"),
                time=formatted_time,
                data=request.form.get("data")
            )
            db.session.add(data)
            db.session.commit()
            return{
                "status":1,
                "message":"举报上传成功！"
            }
        if request.method=='GET':
            data=Report.query.filter(Report.report_user==user).all()
            result=[{
                "id":t.id,
                "available":t.available,
                "reported_user":t.reported_user,
                "message":t.message,
                "time":t.time,
                "score":t.score,
                "data":t.data
            }for t in reversed(data)]
            return{
                "status":1,
                "result":result
            }
        if request.method=='DELETE':
            id=request.headers.get("id")
            data=Report.query.filter_by(id=id).first()
            if data.report_user!=user or not data.available:
                return{
                    "status":0,
                    "message":"未授权"
                }
            db.session.delete(data)
            db.session.commit()
            return{
                "status":1,
                "message":"删除成功"
            }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/admin/admin',methods=['POST','DELETE','GET'])
@jwt_required()
def admin_admin():
    user = get_jwt_identity()
    adminData=Admin.query.filter_by(username=user).first()
    if get_jwt()["role"]!="3" or not adminData.super_admin:
        return{
            "status":0,
            "message":"未授权"
        }
    try:
        if request.method=='GET':
            Data=Admin.query.all()
            result=[{
                "username":t.username,
                "user_manage":t.user_manage,
                "score_manage":t.score_manage,
                "content_manage":t.content_manage,
                "super_admin":t.super_admin,
                "id":t.id
            }for t in Data]
            return{
                "status":1,
                "result":result
            }
        elif request.method=='POST':
            new_id=request.form.get("id")
            if new_id==None:
                new_admin=Admin(
                    username=request.form.get("username"),
                    password=request.form.get("password"),
                    user_manage=True if request.form.get("user_manage") == "1" else False,
                    score_manage=True if request.form.get("score_manage")=="1" else False,
                    content_manage=True if request.form.get("content_manage")=="1" else False,
                    super_admin=True if request.form.get("super_admin")=="1" else False
                )
                db.session.add(new_admin)
                db.session.commit()
                return{
                    "status":1,
                    "message":"添加成功！"
                }
            else:
                new_admin=Admin.query.filter_by(id=new_id).first()
                password=request.form.get("password")
                if password!=None:
                    new_admin.password=password
                new_admin.user_manage=True if request.form.get("user_manage") == "1" else False
                new_admin.score_manage=True if request.form.get("score_manage")=="1" else False
                new_admin.content_manage=True if request.form.get("content_manage")=="1" else False
                new_admin.super_admin=True if request.form.get("super_admin")=="1" else False
                db.session.commit()
                return{
                    "status":1,
                    "message":"修改成功"
                }
        elif request.method=='DELETE':
            id=request.headers.get("id")
            data=Admin.query.filter_by(id=id).first()
            db.session.delete(data)
            db.session.commit()
            return{
                "status":1,
                "message":"删除成功！"
            }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }
@app.route('/admin/setting',methods=['POST','GET'])
@jwt_required()
def admin_setting():
    user = get_jwt_identity()
    adminData=Admin.query.filter_by(username=user).first()
    if get_jwt()["role"]!="3" or not adminData.super_admin:
        return{
            "status":0,
            "message":"未授权"
        }
    try:
        if request.method=='GET':
            set=Setting.query.first()
            return{
                "status":1,
                "result":{
                    "money_per_kg":set.money_per_kg,
                    "rate":set.rate,
                    "score":set.score
                }
            }
        if request.method=='POST':
            set=Setting.query.first()
            set.money_per_kg=request.form.get("money_per_kg")
            set.rate=request.form.get("rate")
            set.score=request.form.get("score")
            db.session.commit()
            return{
                "status":1,
                "message":"修改成功！"
            }
    except Exception as e:
        return {
            "status": 0,
            "message": str(e)
        }