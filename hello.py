# coding: utf8
# 观察者模式
# 从flask框架中导入Flask类
from flask import Flask, render_template, session, request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy

from utils.sql import SQLHelper
from utils.check_winner import checkWinner
# 引入语音识别的类
from utils.speech_recognition import SpeechRecognition
from flask_cors import *
import json



# 传入__name__初始化一个Flask实例
app = Flask(__name__)
app.secret_key = "Serect Key"

# 指定连接字符串
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:123456@localhost:3306/flask'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

# 解决跨域

# 创建SQLAlchemy的实例
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('login.html')

# app.route装饰器映射URL和执行的函数。这个设置将根URL映射到了hello_world函数上
@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    user=request.form.get('user')
    pwd=request.form.get('pwd')

    # 调用封装的类返回数据
    obj=SQLHelper.fetch_one('select id,password from users where name=%s and password=%s', [user, pwd, ])
    if obj:
        session.permanet = True
        session['user_info'] = {'id': obj['id'], 'name': user}
        # return redirect('/success')id int;pwd varchar
        return redirect('/success')
    else:
        return render_template('login.html',msg='用户名或密码错误')

@app.route('/success',methods=['GET','POST'])
@cross_origin()
def success():
    # id int;chessx int;chessy int;color int；0代表黑色，1代表白色

    userinfo = session['user_info']  #存储用户信息

    objchess = SQLHelper.fetch_all('select chessx,chessy,color from chess where userid=%s', [userinfo['id'], ])

    return render_template('success.html',objchess=json.dumps(objchess),name=userinfo['name'])

@app.route('/insert',methods=['GET','POST'])
@cross_origin()
def insert():
    userinfo = session['user_info']  # 存储用户信息
    data = request.get_json()  # 获取前端传过来的参数
    if (data != None):
        # 向数据库插入数据
        sql = 'insert into chess values(%s,%s,%s,%s)'
        SQLHelper.dbChange(sql,[userinfo['id'],data['chessx'],data['chessy'],data['color'],])
        # 进行判断
        result = checkWinner.check_winner(data)
        # print(result)
        if result >= 4:
            return '111'
        else:
            # print('测试在这')
            return '000'

    else:
        return redirect('/failure')

@app.route('/failure',methods=['GET','POST'])
@cross_origin()
def failure():
    # end = request.get_json()
    # print(end)
    # 游戏失败删除数据库中数据
    userinfo = session['user_info']  # 存储用户信息
    sql = 'delete from chess where userid=%s'
    SQLHelper.dbChange(sql,[userinfo['id'],])
    return render_template('failure.html')

@app.route('/PlayorBack',methods=['GET','POST'])
@cross_origin()
def PlayorBack():
    end = request.get_json()
    # print(end['replay'])
    if end['replay'] == 1:
        print('111111111')
        # return redirect('/success')
        return '11'
    else:
        print(22222)
        return '0'

@app.route('/speechRecognition', methods=['GET', 'POST'])
@cross_origin()
def speechRecognition():
    # 当按钮点击时调用语音识别的方法
    result = SpeechRecognition.speechRecognition()
    # print(result)
    # 获取坐标和颜色
    x = int(result[0])
    y = int(result[1])
    color = int(result[2])
    # print(x,'--',y,'--',color)
    userinfo = session['user_info']  # 存储用户信息
    # 向数据库插入数据
    sql = 'insert into chess values(%s,%s,%s,%s)'
    SQLHelper.dbChange(sql, [userinfo['id'], x, y, color, ])
    objchess = SQLHelper.fetch_all('select chessx,chessy,color from chess where userid=%s', [userinfo['id'], ])

    return render_template('success.html', objchess=json.dumps(objchess), name=userinfo['name'])

if __name__ == '__main__':
    # 运行本项目，host=0.0.0.0可以让其他电脑也能访问到该网站，port指定访问的端口。默认的host是127.0.0.1，port为5000
    # app.run(host='0.0.0.0', port=9000)
    app.run(debug=True)