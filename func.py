from app.database import db, Stu, Booker,Setting, Admin,app
from werkzeug.security import check_password_hash
def check_login(username_input, password):
    user = Stu.query.filter_by(username=username_input).first()
    setting=Setting.query.first().score
    if not user:
        return False
    if int(user.score)<int(setting):
        return False
    return check_password_hash(user.password,password)
def check_score_ava(score):
    setting=Setting.query.first().score
    return score>=setting
def check_booker_login(username,password):
    user=Booker.query.filter_by(username=username).first()
    if not user:
        return False
    return check_password_hash(user.password,password)
def check_admin_login(username,password):
    user=Admin.query.filter_by(username=username).first()
    if not user:
        return False
    return check_password_hash(user.password,password)
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