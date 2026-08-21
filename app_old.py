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
from voice import speech_to_text
from voice_ai import correct_voice_text
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

    add_file_message,

    add_voice_message,

    get_unread_count,

    read_messages,

    withdraw_message,

    get_message,

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



    if diff < 60:

        return "刚刚"



    if diff < 3600:

        return f"{int(diff/60)}分钟前"



    if diff < 86400:

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



        user=get_user(
            username
        )



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

                request.headers.get(
                    "User-Agent"
                )

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







# ==========================
# 在线状态
# ==========================

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



        # 30秒没有心跳自动离线

        if (

            data["online"]==1

            and

            time.time()-last<=30

        ):

            online=True




    return jsonify({

        "online":online,

        "text":

        "在线"

        if online

        else

        "离线",

        "last":

        format_time(last)

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








# ==========================
# 聊天页面
# ==========================

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








# ==========================
# 获取消息
# ==========================

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

            "id":msg["id"],

            "sender":msg["sender"],

            "content":msg["content"],

            "type":msg["type"],

            "time":msg["created"],

            "withdrawn":msg["withdrawn"],

            "withdraw_time":msg["withdraw_time"],
        
            "quote_id":msg["quote_id"],
       
            "quote_text":msg["quote_text"],

            "voice_text":msg["voice_text"]


        })




    read_messages(
        username
    )



    return jsonify(
        result
    )









# ==========================
# 未读
# ==========================

@app.route("/chat/unread")
@login_required
def chat_unread():


    return jsonify({

        "count":

        get_unread_count(

            session["user"]

        )

    })









# ==========================
# 图片上传
# ==========================

@app.route(
    "/chat/upload",
    methods=["POST"]
)

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
# ==========================
# 文件上传
# ==========================

@app.route(
    "/chat/file/upload",
    methods=["POST"]
)

@login_required
def chat_file_upload():


    file=request.files.get(
        "file"
    )



    if not file:

        return jsonify({

            "success":False

        })



    sender=session["user"]


    receiver=get_other_user(
        sender
    )



    folder="static/uploads/file"



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



    add_file_message(

        sender,

        receiver,

        filename

    )



    return jsonify({

        "success":True

    })








# ==========================
# 拍照上传
# ==========================

@app.route(
    "/chat/camera",
    methods=["POST"]
)

@login_required
def camera_upload():


    file=request.files.get(
        "camera"
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

        "camera_"

        +

        str(int(time.time()))

        +

        ".jpg"

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









# ==========================
# 语音上传 + Whisper + AI上下文纠错
# ==========================

@app.route(
    "/chat/voice",
    methods=["POST"]
)
@login_required
def voice_upload():

    file=request.files.get(
        "voice"
    )

    if not file:
        return jsonify({
            "success":False
        })


    sender=session["user"]

    receiver=get_other_user(
        sender
    )


    folder="static/uploads/voice"

    os.makedirs(
        folder,
        exist_ok=True
    )


    filename=(
        "voice_"
        +
        str(int(time.time()))
        +
        ".webm"
    )


    path=os.path.join(
        folder,
        filename
    )


    file.save(
        path
    )


    text=""


    try:

        # Whisper识别
        text=speech_to_text(
            path
        )


        # 获取最近聊天记录作为上下文
        messages=get_messages(
            sender,
            receiver
        )


        history=""


        for msg in messages[-20:]:

            history += (
                msg["sender"]
                +
                ":"
                +
                msg["content"]
                +
                "\n"
            )


        # AI上下文纠错
        from voice_context_ai import correct_with_context


        text=correct_with_context(
            text,
            history
        )


    except Exception as e:

        print(
            "语音AI处理失败:",
            e
        )


    add_voice_message(
        sender,
        receiver,
        filename,
        text
    )


    return jsonify({
        "success":True
    })
# ==========================
# 撤回消息
# ==========================

@app.route(
    "/chat/withdraw/<int:message_id>",
    methods=["POST"]
)

@login_required
def chat_withdraw(message_id):


    msg=get_message(
        message_id
    )



    if not msg:

        return jsonify({

            "success":False

        })



    if msg["sender"] != session["user"]:

        return jsonify({

            "success":False

        })



    withdraw_message(
        message_id
    )



    return jsonify({

        "success":True

    })








# ==========================
# 发送引用消息
# ==========================

@app.route(
    "/chat/quote",
    methods=["POST"]
)

@login_required
def chat_quote():


    data=request.json



    content=data.get(
        "content",
        ""
    )


    quote_id=data.get(
        "quote_id",
        0
    )


    quote_text=data.get(
        "quote_text",
        ""
    )



    sender=session["user"]


    receiver=get_other_user(
        sender
    )



    add_message(

        sender,

        receiver,

        content,

        "text",

        quote_id,

        quote_text

    )



    return jsonify({

        "success":True

    })









# ==========================
# Socket实时消息
# ==========================

@socketio.on(
    "send_message"
)

def socket_send(data):


    sender=data.get(
        "sender"
    )


    content=data.get(
        "content"
    )



    msg_type=data.get(
        "type",
        "text"
    )



    receiver=get_other_user(
        sender
    )



    message_id=add_message(

        sender,

        receiver,

        content,

        msg_type

    )



    emit(

        "receive_message",

        {

            "id":message_id,

            "sender":sender,

            "content":content,

            "type":msg_type,

            "time":datetime.now().strftime(

                "%Y-%m-%d %H:%M"

            )

        },

        broadcast=True

    )
# ==========================
# 个人资料
# ==========================

@app.route(
    "/profile",
    methods=["GET","POST"]
)

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







# ==========================
# 管理后台
# ==========================

@app.route(
    "/admin",
    methods=["GET","POST"]
)

def admin_login():


    if request.method=="POST":


        username=request.form.get(
            "username"
        )


        password=request.form.get(
            "password"
        )



        if (

            username==ADMIN_USERNAME

            and

            password==ADMIN_PASSWORD

        ):


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
            "%H:%M"
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







# ==========================
# 登出
# ==========================

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