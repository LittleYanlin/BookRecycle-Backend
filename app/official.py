from flask import Blueprint, request
bp=Blueprint('official', __name__, url_prefix='/official')
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt
from sqlalchemy import and_
from app.database import db, Stu, Booker, Book_Recycle, Setting
from func import check_score_ava
from datetime import datetime
@bp.route('/getBooks', methods=['GET'])#显示旧书回收模块
@jwt_required()
def get_other_books():
    try:
        username=get_jwt_identity()
        action=request.headers.get("Action")
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
@bp.route('/shoushu',methods=['POST'])
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
@bp.route('/uploadBooks', methods=['POST'])
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
@bp.route("/getOrder",methods=['POST'])
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
@bp.route("/getOrderDetail",methods=['GET'])
@jwt_required()
def get_order_detail():
    try:
        user = get_jwt_identity()
        data=Book_Recycle.query.filter_by(id=request.headers.get("id")).first()
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