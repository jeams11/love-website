# app.py 最终版（第 1/3）

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit
from functools import wraps
from datetime import datetime

import time
import os
import psutil
import platform


from database import (
    init_db,
    get_db,
    add_user,
    get_user,
    update_status,
    get_status,
    add_login_log,
    add_device,
    add_visit,
    get_login_logs,
    get_devices,
    get_visit_count,
    get_today_visit_count,
    add_message,
    get_messages,
    add_image_message,
    get_unread_count,
    create_profile,
    get_profile,
    update_profile,
    update_avatar
)


app = Flask(__name__)

app.secret_key = "love-website-secret-key"


bcrypt = Bcrypt(app)


socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)


ADMIN_USERNAME="admin"
ADMIN_PASSWORD="101221"


system_history=[]


init_db()



def create_default_users():

    users={
        "泽泽":"110702",
        "真真":"110202"
    }


    for username,password in users.items():

        user=get_user(username)


        if not user:

            hashed=bcrypt.generate_password_hash(
                password
            ).decode("utf-8")


            add_user(
                username,
                hashed
            )


        create_profile(username)



create_default_users()



def login_required(func):

    @wraps(func)
    def wrapper(*args,**kwargs):

        if "user" not in session:

            return redirect(
                url_for("login")
            )

        return func(
            *args,
            **kwargs
        )

    return wrapper




def admin_required(func):

    @wraps(func)
    def wrapper(*args,**kwargs):

        if not session.get("admin"):

            return redirect(
                url_for("admin_login")
            )

        return func(
            *args,
            **kwargs
        )

    return wrapper





def get_other_user(username):

    return "真真" if username=="泽泽" else "泽泽"




def format_time(timestamp):

    if not timestamp:
        return "暂无记录"


    diff=time.time()-timestamp


    if diff<60:
        return "刚刚"


    if diff<3600:
        return f"{int(diff/60)}分钟前"


    if diff<86400:
        return f"{int(diff/3600)}小时前"


    return datetime.fromtimestamp(
        timestamp
    ).strftime(
        "%m月%d日 %H:%M"
    )





@app.route("/",methods=["GET","POST"])
@app.route("/login",methods=["GET","POST"])
def login():

    add_visit(
        request.remote_addr
    )


    if request.method=="POST":

        username=request.form.get(
            "username"
        )

        password=request.form.get(
            "password"
        )


        user=get_user(username)


        if user and bcrypt.check_password_hash(
            user["password"],
            password
        ):


            session["user"]=username


            update_status(
                username,
                1
            )


            add_login_log(
                username,
                request.remote_addr,
                request.headers.get("User-Agent")
            )


            return redirect(
                url_for("home")
            )


    return render_template(
        "login.html"
    )





@app.route("/home")
@login_required
def home():

    username=session["user"]

    other=get_other_user(
        username
    )


    profile=get_profile(
        username
    )


    other_profile=get_profile(
        other
    )


    start=datetime(
        2026,
        6,
        5
    )


    days=(
        datetime.now()
        -
        start
    ).days



    conn=get_db()


    memories=conn.execute(
        """
        SELECT *
        FROM memories
        ORDER BY id DESC
        """
    ).fetchall()


    conn.close()



    return render_template(

        "home.html",

        user=username,

        other=other,

        profile=profile,

        other_profile=other_profile,

        days=days,

        start_date="2026年6月5日 星期五",

        memories=memories

    )
# app.py 最终版（第 2/3）

@app.route("/status")
@login_required
def status():

    other=get_other_user(
        session["user"]
    )


    data=get_status(
        other
    )


    online=False
    last=0


    if data:

        last=data["last_time"]


        if data["online"]==1 and time.time()-last<=30:

            online=True



    return jsonify({

        "online":online,

        "last":format_time(last)

    })





@app.route("/heartbeat")
@login_required
def heartbeat():

    update_status(
        session["user"],
        1
    )


    return jsonify({
        "success":True
    })






@app.route("/chat")
@login_required
def chat():

    username=session["user"]


    other=get_other_user(
        username
    )


    other_profile=get_profile(
        other
    )


    return render_template(

        "chat.html",

        user=username,

        other=other,

        other_profile=other_profile

    )






@app.route("/chat/send",methods=["POST"])
@login_required
def chat_send():

    sender=session["user"]


    data=request.json


    content=data.get(
        "content",
        ""
    )


    if not content.strip():

        return jsonify({
            "success":False
        })


    receiver=get_other_user(
        sender
    )


    add_message(
        sender,
        receiver,
        content
    )


    return jsonify({
        "success":True
    })






@app.route("/chat/messages")
@login_required
def chat_messages():

    username=session["user"]


    other=get_other_user(
        username
    )


    messages=get_messages(
        username,
        other
    )


    result=[]


    for msg in messages:

        result.append({

            "sender":msg["sender"],

            "content":msg["content"],

            "type":msg["type"],

            "time":msg["created"]

        })


    return jsonify(result)






@app.route("/chat/unread")
@login_required
def chat_unread():

    return jsonify({

        "count":
        get_unread_count(
            session["user"]
        )

    })







@app.route("/chat/upload",methods=["POST"])
@login_required
def chat_upload():

    file=request.files.get(
        "image"
    )


    if not file:

        return jsonify({
            "success":False
        })


    sender=session["user"]


    receiver=get_other_user(
        sender
    )


    folder="static/uploads/chat"


    os.makedirs(
        folder,
        exist_ok=True
    )


    filename=(

        str(int(time.time()))

        +

        "_"

        +

        file.filename

    )


    file.save(
        os.path.join(
            folder,
            filename
        )
    )


    add_image_message(
        sender,
        receiver,
        filename
    )


    return jsonify({

        "success":True

    })








@app.route("/profile",methods=["GET","POST"])
@login_required
def profile():

    username=session["user"]


    if request.method=="POST":


        nickname=request.form.get(
            "nickname"
        )


        birthday_type=request.form.get(
            "birthday_type",
            "solar"
        )


        birthday=request.form.get(
            "birthday",
            ""
        )


        lunar_month=request.form.get(
            "lunar_month",
            ""
        )


        lunar_day=request.form.get(
            "lunar_day",
            ""
        )


        lunar_solar_date=request.form.get(
            "lunar_solar_date",
            ""
        )


        signature=request.form.get(
            "signature",
            ""
        )



        update_profile(

            username,

            nickname,

            birthday_type,

            birthday,

            lunar_month,

            lunar_day,

            lunar_solar_date,

            signature

        )



        avatar=request.files.get(
            "avatar"
        )


        if avatar and avatar.filename:


            folder="static/uploads/avatar"


            os.makedirs(
                folder,
                exist_ok=True
            )


            filename=(

                username

                +

                "_"

                +

                str(int(time.time()))

                +

                ".png"

            )


            avatar.save(
                os.path.join(
                    folder,
                    filename
                )
            )


            update_avatar(
                username,
                filename
            )



        return redirect(
            url_for("profile")
        )


    return render_template(

        "profile.html",

        profile=get_profile(
            username
        )

    )
# app.py 最终版（第 3/3）

@socketio.on("send_message")
def socket_send(data):

    sender=data.get(
        "sender"
    )

    content=data.get(
        "content"
    )


    receiver=get_other_user(
        sender
    )


    add_message(
        sender,
        receiver,
        content
    )


    emit(

        "receive_message",

        {

            "sender":sender,

            "content":content,

            "time":datetime.now().strftime(
                "%H:%M"
            )

        },

        broadcast=True

    )







@app.route("/admin",methods=["GET","POST"])
def admin_login():

    if request.method=="POST":

        username=request.form.get(
            "username"
        )

        password=request.form.get(
            "password"
        )


        if username==ADMIN_USERNAME and password==ADMIN_PASSWORD:

            session["admin"]=True


            return redirect(
                url_for(
                    "admin_dashboard"
                )
            )


    return render_template(
        "admin_login.html"
    )







@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    return render_template(

        "admin.html",

        logs=get_login_logs(),

        devices=get_devices()

    )






@app.route("/admin/system")
@admin_required
def system_status():

    cpu=psutil.cpu_percent()


    system_history.append({

        "time":datetime.now().strftime(
            "%H:%M:%S"
        ),

        "cpu":cpu

    })


    if len(system_history)>60:

        system_history.pop(0)



    return jsonify({

        "cpu":cpu,

        "memory":
        psutil.virtual_memory().percent,

        "disk":
        psutil.disk_usage("/").percent,

        "system":
        platform.system(),

        "machine":
        platform.machine()

    })







@app.route("/admin/system/history")
@admin_required
def system_history_api():

    return jsonify(
        system_history
    )







@app.route("/admin/stats")
@admin_required
def admin_stats():

    return jsonify({

        "visits":
        get_visit_count(),

        "today":
        get_today_visit_count()

    })







@app.route("/admin/tunnel")
@admin_required
def admin_tunnel():

    return jsonify({

        "status":"running"

    })







@app.route("/logout")
def logout():

    if "user" in session:

        update_status(
            session["user"],
            0
        )


    session.clear()


    return redirect(
        url_for("login")
    )








if __name__=="__main__":


    socketio.run(

        app,

        host="0.0.0.0",

        port=9000

    )