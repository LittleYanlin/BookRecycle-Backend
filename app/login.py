from flask import Blueprint
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token
from app.database import db, Stu, Booker
from func import check_login,check_booker_login,check_admin_login
from werkzeug.security import generate_password_hash
from check import *
bp=Blueprint('login', __name__)
@bp.route('/login', methods=['POST'])
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
        if not check_password(password):
            return {
                "status": 0,
                "message": "密码格式错误！"
            }
        if role=="1":
            if not check_username(username):
                return {
                    "status": 0,
                    "message": "用户名格式错误！"
                }
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
            if not check_username(username):
                return {
                    "status": 0,
                    "message": "用户名格式错误！"
                }
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
@bp.route('/check_first_login',methods=['POST'])
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
@bp.route("/reg",methods=['POST'])
def reg():
    try:
        reg_role=request.form.get("role")
        password=generate_password_hash(request.form.get("password"))
        if not password or not request.form.get("username") or not request.form.get("role"):
            return{
                "status":0,
                "message":"请检查你的输入内容"
            }
        if not check_password(request.form.get("password")):
            return {
                "status": 0,
                "message": "密码格式错误！"
            }
        if not check_username(request.form.get("username")):
            return {
                "status": 0,
                "message": "用户名格式错误！"
            }
        if not check_phone(request.form.get("phone")):
            return {
                "status": 0,
                "message": "手机号格式错误！"
            }
        if reg_role=="1":
            new_user=Stu(
                username=request.form.get("username"),
                password=password,
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
            if not check_name(request.form.get("name")):
                return {
                    "status": 0,
                    "message": "姓名格式错误！"
                }
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