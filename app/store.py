from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.database import db, Stu, Book_Upload, Report
from sqlalchemy import and_
from flask import request
from datetime import datetime
from func import check_score_ava
bp=Blueprint('store', __name__,url_prefix='/store')
@bp.route('/getBooks', methods=['GET'])#旧书再利用模块
@jwt_required()
def get_books():
    try:
        username=get_jwt_identity()
        user=Stu.query.filter_by(username=username).first()
        action=request.headers.get("Action")
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
@bp.route("/uploadBooks",methods=['POST'])
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
@bp.route("/bookEnd",methods=['GET'])
@jwt_required()
def book_end():
    try:
        user = get_jwt_identity()
        data=Book_Upload.query.filter_by(id=request.headers.get("id")).first()
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
@bp.route('/report',methods=['POST','DELETE','GET'])
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