from flask import Flask, session, redirect, url_for, request
from flask_bcrypt import Bcrypt

from extensions import socketio

from database import (
    init_db,
    get_user,
    add_user,
    create_profile,
    add_visit,
    update_status
)

from routes.auth import auth_bp
from routes.home import home_bp
from routes.chat import chat_bp
from routes.voice import voice_bp

import os



app = Flask(__name__)


app.secret_key = "love-website-secret-key"


bcrypt = Bcrypt(app)



# ==========================
# 注册路由模块
# ==========================

app.register_blueprint(
    auth_bp
)


app.register_blueprint(
    home_bp
)


app.register_blueprint(
    chat_bp
)


app.register_blueprint(
    voice_bp
)




# ==========================
# 初始化数据库
# ==========================

init_db()





# ==========================
# 默认用户
# ==========================

def create_default_users():


    users = {

        "泽泽":"110702",

        "真真":"110202"

    }



    for username,password in users.items():


        user=get_user(
            username
        )


        if not user:


            hashed=bcrypt.generate_password_hash(
                password
            ).decode(
                "utf-8"
            )


            add_user(

                username,

                hashed

            )


        create_profile(
            username
        )




create_default_users()







# ==========================
# 全局访问统计
# ==========================

@app.before_request
def record_visit():


    # 静态文件不统计

    if request.path.startswith(
        "/static"
    ):

        return



    try:

        add_visit(
            request.remote_addr
        )

    except:

        pass





# ==========================
# 登出
# ==========================

@app.route(
    "/logout"
)

def logout():


    if "user" in session:


        update_status(

            session["user"],

            0

        )



    session.clear()



    return redirect(
        url_for("auth.login")
    )







# ==========================
# 启动
# ==========================

if __name__ == "__main__":


    socketio.init_app(
        app,
        cors_allowed_origins="*"
    )


    socketio.run(

        app,

        host="0.0.0.0",

        port=9000

    )