from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
bp=Blueprint('admin', __name__, url_prefix='/admin')
from app.database import db, Stu,Setting, Admin, Chat, Book_Upload, Report, Reason
from datetime import datetime
@bp.route("/user/stu",methods=['GET'])
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
@bp.route("/user/stuManage",methods=['POST'])
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
@bp.route('/score',methods=['GET'])
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
@bp.route('/scoreManage',methods=['POST'])
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
@bp.route('/reason', methods=['GET', 'POST', 'DELETE'])
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
@bp.route('/scoreCancel',methods=['POST'])
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
@bp.route('/bookManage',methods=['POST','GET','DELETE'])
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
@bp.route('/admin',methods=['POST','DELETE','GET'])
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
@bp.route('/setting',methods=['POST','GET'])
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