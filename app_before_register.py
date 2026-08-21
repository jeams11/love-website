from flask import Flask

from database import init_db

from extensions import (
    bcrypt,
    socketio
)


from routes.auth import auth_bp
from routes.home import home_bp
from routes.chat import chat_bp
from routes.voice import voice_bp
from routes.profile import profile_bp
from routes.admin import admin_bp



app = Flask(__name__)


app.secret_key = "love-website-secret-key"



bcrypt.init_app(
    app
)


socketio.init_app(
    app
)



init_db()



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



if __name__=="__main__":

    socketio.run(

        app,

        host="0.0.0.0",

        port=9000

    )
