'''
Author: LittleYanlin
Date: 2025-05-08 21:59:27
Version: 1.1.0
'''
from app.database import app,db,Setting,Admin
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity , get_jwt
from flask import request,send_from_directory,url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os
import time
import uuid
from datetime import datetime
from func import allowed_file
from app.database import Img
from app.login import bp as login_bp
from app.official import bp as official_bp
from app.chat import bp as chat_bp
from app.manage import bp as manage_bp
from app.store import bp as store_bp
from app.admin import bp as admin_bp
app.register_blueprint(login_bp)
app.register_blueprint(official_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(manage_bp)
app.register_blueprint(store_bp)
app.register_blueprint(admin_bp)
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
        password=generate_password_hash("abc123456"),
        user_manage=True,
        score_manage=True,
        content_manage=True,
        super_admin=True
    )
    db.session.add(admin)
    db.session.add(setting)
    db.session.commit()
@app.route('/')
def index():
    return "后端启动成功！"
@app.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)  # 必须提供 refresh_token
def refresh():
    current_user = get_jwt_identity()
    role=get_jwt()["role"]
    new_access_token = create_access_token(identity=str(current_user),additional_claims={"role":role})
    return{
        "status":1,
        "access_token":new_access_token
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
            filepath = os.path.join("app/"+app.config['UPLOAD_FOLDER'], unique_filename)
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
if __name__=="__main__":
    app.run(debug=True)