from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
bp=Blueprint('chat', __name__, url_prefix='/chat')
from app.database import db,Chat
from func import manage_data
from sqlalchemy import and_, or_
from datetime import datetime
@bp.route("/get/all",methods=['GET'])
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
@bp.route("/get/detail",methods=['GET'])
@jwt_required()
def get_data_detail():
    try:
        request_user=request.headers.get("ReqUser")
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
@bp.route("/post",methods=['POST'])
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