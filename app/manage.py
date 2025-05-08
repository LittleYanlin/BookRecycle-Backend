from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.database import db, Stu, Booker,Admin
from werkzeug.security import generate_password_hash
from check import *
bp=Blueprint('manage', __name__, url_prefix='/manage')
@bp.route("/1",methods=['POST','GET'])
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
        if action=='check' or request.method=='GET':
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
            if not check_password(new_pass):
                return {
                    "status": 0,
                    "message": "密码格式错误！"
                }
            userData.password=generate_password_hash(new_pass)
        if not check_phone(request.form.get("phone")):
            return {
                "status": 0,
                "message": "手机号格式错误！"
            }
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
@bp.route("/2",methods=['POST','GET'])
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
        if action=='check' or request.method=='GET':
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
            if not check_password(new_pass):
                return {
                    "status": 0,
                    "message": "密码格式错误！"
                }
            userData.password=generate_password_hash(new_pass)
        if not check_phone(request.form.get("phone")):
            return {
                "status": 0,
                "message": "手机号格式错误！"
            }
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
@bp.route("/3",methods=['POST','GET'])
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
        if action=='check' or request.method=='GET':
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
            if not check_password(new_pass):
                return {
                    "status": 0,
                    "message": "密码格式错误！"
                }
            userData.password=generate_password_hash(new_pass)
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