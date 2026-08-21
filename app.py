from flask import Flask

from flask_bcrypt import Bcrypt

from extensions import socketio

from database import (
    init_db,
    add_user,
    get_user,
    create_profile
)

from routes.auth import auth_bp
from routes.home import home_bp
from routes.chat import chat_bp
from routes.voice import voice_bp
from routes.profile import profile_bp
from routes.admin import admin_bp

# Socket事件
import routes.chat_status


app = Flask(__name__)


app.secret_key = "love-website-secret-key"



bcrypt = Bcrypt(app)





# ==========================
# 初始化数据库
# ==========================

init_db()





# ==========================
# 创建默认账号
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
# 注册蓝图
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


app.register_blueprint(
    profile_bp
)


app.register_blueprint(
    admin_bp
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