from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

from functools import wraps
from datetime import datetime

import os
import time

from werkzeug.utils import secure_filename

from database import (
    get_messages,
    get_profile,
    get_unread_count,
    read_messages,
    add_message,
    add_image_message,
    add_file_message,
    add_voice_message,
    get_message,
    withdraw_message
)

from extensions import socketio

from flask_socketio import emit


chat_bp = Blueprint(
    "chat",
    __name__
)


# ==========================
# 上传配置
# ==========================

UPLOAD_IMAGE = "static/uploads/chat"
UPLOAD_FILE = "static/uploads/file"
UPLOAD_VOICE = "static/uploads/voice"


MAX_FILE_SIZE = 50 * 1024 * 1024


ALLOWED_IMAGE = {
    "png",
    "jpg",
    "jpeg",
    "gif",
    "webp"
}


ALLOWED_FILE = {
    "pdf",
    "txt",
    "doc",
    "docx",
    "zip",
    "rar"
}


# ==========================
# 登录验证
# ==========================

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user" not in session:

            return redirect(
                url_for(
                    "auth.login"
                )
            )

        return func(
            *args,
            **kwargs
        )

    return wrapper



# ==========================
# 获取聊天对象
# ==========================

def get_other_user(username):

    return (
        "真真"
        if username == "泽泽"
        else
        "泽泽"
    )



# ==========================
# 文件安全检测
# ==========================

def get_extension(filename):

    if "." not in filename:

        return ""

    return filename.rsplit(
        ".",
        1
    )[1].lower()



def check_image(filename):

    return (
        get_extension(filename)
        in
        ALLOWED_IMAGE
    )



def check_file(filename):

    return (
        get_extension(filename)
        in
        ALLOWED_FILE
    )



def check_size(file):

    file.seek(
        0,
        2
    )

    size = file.tell()

    file.seek(
        0
    )

    return size <= MAX_FILE_SIZE



def create_filename(filename):

    filename = secure_filename(
        filename
    )


    ext = ""


    if "." in filename:

        ext = "." + filename.rsplit(
            ".",
            1
        )[1]


    return (

        str(
            int(
                time.time()*1000
            )
        )

        +

        "_"

        +

        filename[:80]

    )



def save_upload_file(
    file,
    folder
):

    if not check_size(file):

        return None


    os.makedirs(
        folder,
        exist_ok=True
    )


    filename = create_filename(
        file.filename
    )


    path = os.path.join(
        folder,
        filename
    )


    file.save(
        path
    )


    return filename



# ==========================
# 聊天页面
# ==========================

@chat_bp.route(
    "/chat"
)
@login_required
def chat():

    username = session["user"]


    other = get_other_user(
        username
    )


    return render_template(

        "chat.html",

        user=username,

        other=other,

        other_profile=get_profile(
            other
        )

    )



# ==========================
# 获取消息
# ==========================

@chat_bp.route(
    "/chat/messages"
)
@login_required
def chat_messages():

    username = session["user"]


    other = get_other_user(
        username
    )


    messages = get_messages(
        username,
        other
    )


    result = []


    for msg in messages:

        result.append({

            "id": msg["id"],

            "sender": msg["sender"],

            "content": msg["content"],

            "type": msg["type"],

            "time": msg["created"],

            "withdrawn": msg["withdrawn"],

            "withdraw_time": msg["withdraw_time"],

            "quote_id": msg["quote_id"],

            "quote_text": msg["quote_text"],

            "voice_text": msg["voice_text"]

        })


    read_messages(
        username
    )


    return jsonify(
        result
    )



# ==========================
# 未读消息
# ==========================

@chat_bp.route(
    "/chat/unread"
)
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

@chat_bp.route(
    "/chat/upload",
    methods=["POST"]
)
@login_required
def chat_upload():

    file = request.files.get(
        "image"
    )


    if not file:

        return jsonify({
            "success":False
        })


    if not check_image(
        file.filename
    ):

        return jsonify({

            "success":False,

            "error":"图片格式错误"

        })


    filename = save_upload_file(

        file,

        UPLOAD_IMAGE

    )


    if not filename:

        return jsonify({

            "success":False,

            "error":"文件过大"

        })


    sender = session["user"]

    receiver = get_other_user(
        sender
    )


    add_image_message(

        sender,

        receiver,

        filename

    )


    return jsonify({

        "success":True,

        "filename":filename

    })
# ==========================
# 文件上传
# ==========================

@chat_bp.route(
    "/chat/file/upload",
    methods=["POST"]
)
@login_required
def chat_file_upload():

    file = request.files.get(
        "file"
    )


    if not file:

        return jsonify({

            "success":False

        })


    if not check_file(
        file.filename
    ):

        return jsonify({

            "success":False,

            "error":"文件格式不支持"

        })


    filename = save_upload_file(

        file,

        UPLOAD_FILE

    )


    if not filename:

        return jsonify({

            "success":False,

            "error":"文件过大"

        })


    sender = session["user"]


    receiver = get_other_user(
        sender
    )


    add_file_message(

        sender,

        receiver,

        filename

    )


    return jsonify({

        "success":True,

        "filename":filename

    })



# ==========================
# 语音上传
# ==========================

@chat_bp.route(
    "/chat/voice",
    methods=["POST"]
)
@login_required
def chat_voice():

    file = request.files.get(
        "voice"
    )


    if not file:

        return jsonify({

            "success":False

        })


    if not check_size(file):

        return jsonify({

            "success":False,

            "error":"语音过大"

        })


    os.makedirs(

        UPLOAD_VOICE,

        exist_ok=True

    )


    filename = (

        "voice_"

        +

        str(
            int(
                time.time()*1000
            )
        )

        +

        ".webm"

    )


    path = os.path.join(

        UPLOAD_VOICE,

        filename

    )


    file.save(
        path
    )


    sender = session["user"]


    receiver = get_other_user(
        sender
    )


    add_voice_message(

        sender,

        receiver,

        filename

    )


    return jsonify({

        "success":True,

        "filename":filename

    })



# ==========================
# 摄像头拍照上传
# ==========================

@chat_bp.route(
    "/chat/camera",
    methods=["POST"]
)
@login_required
def camera_upload():

    file = request.files.get(
        "camera"
    )


    if not file:

        return jsonify({

            "success":False

        })


    if not check_size(file):

        return jsonify({

            "success":False,

            "error":"图片过大"

        })


    os.makedirs(

        UPLOAD_IMAGE,

        exist_ok=True

    )


    filename = (

        "camera_"

        +

        str(
            int(
                time.time()*1000
            )
        )

        +

        ".jpg"

    )


    file.save(

        os.path.join(

            UPLOAD_IMAGE,

            filename

        )

    )


    sender = session["user"]


    receiver = get_other_user(
        sender
    )


    add_image_message(

        sender,

        receiver,

        filename

    )


    return jsonify({

        "success":True,

        "filename":filename

    })



# ==========================
# 撤回消息
# ==========================

@chat_bp.route(
    "/chat/withdraw/<int:message_id>",
    methods=["POST"]
)
@login_required
def chat_withdraw(message_id):

    msg = get_message(
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


    emit(

        "withdraw_message",

        {

            "id":message_id

        },

        broadcast=True

    )


    return jsonify({

        "success":True

    })



# ==========================
# 引用消息
# ==========================

@chat_bp.route(
    "/chat/quote",
    methods=["POST"]
)
@login_required
def chat_quote():

    data = request.json or {}


    content = data.get(
        "content",
        ""
    )


    quote_id = data.get(
        "quote_id",
        0
    )


    quote_text = data.get(
        "quote_text",
        ""
    )


    if not content:

        return jsonify({

            "success":False

        })


    sender = session["user"]


    receiver = get_other_user(
        sender
    )


    message_id = add_message(

        sender,

        receiver,

        content,

        "text",

        quote_id,

        quote_text

    )


    message = {

        "id":message_id,

        "sender":sender,

        "content":content,

        "type":"text",

        "time":

        datetime.now().strftime(

            "%Y-%m-%d %H:%M:%S"

        ),

        "withdrawn":0,

        "quote_id":quote_id,

        "quote_text":quote_text,

        "voice_text":""

    }


    emit(

        "receive_message",

        message,

        broadcast=True

    )


    return jsonify({

        "success":True

    })

# ==========================
# Socket 实时聊天
# ==========================

@socketio.on(
    "send_message"
)
def socket_send(data):

    sender = session.get(
        "user"
    )


    if not sender:

        return



    if not data:

        return



    content = data.get(
        "content",
        ""
    )


    msg_type = data.get(
        "type",
        "text"
    )


    quote_id = data.get(
        "quote_id",
        0
    )


    quote_text = data.get(
        "quote_text",
        ""
    )



    # 文本消息不能为空
    # 图片/文件/语音允许为空
    if msg_type == "text" and not content:

        return



    receiver = get_other_user(
        sender
    )



    message_id = add_message(

        sender,

        receiver,

        content,

        msg_type,

        quote_id,

        quote_text

    )



    message = {

        "id": message_id,

        "sender": sender,

        "content": content,

        "type": msg_type,

        "time":

        datetime.now().strftime(

            "%Y-%m-%d %H:%M:%S"

        ),

        "withdrawn": 0,

        "withdraw_time": "",

        "quote_id": quote_id,

        "quote_text": quote_text,

        "voice_text": ""

    }



    emit(

        "receive_message",

        message,

        broadcast=True

    )



# ==========================
# Socket 撤回同步
# ==========================

@socketio.on(
    "withdraw_message"
)
def socket_withdraw(data):

    sender = session.get(
        "user"
    )


    if not sender:

        return



    message_id = data.get(
        "id"
    )


    if not message_id:

        return



    msg = get_message(
        message_id
    )


    if not msg:

        return



    if msg["sender"] != sender:

        return



    withdraw_message(
        message_id
    )


    emit(

        "withdraw_message",

        {

            "id": message_id

        },

        broadcast=True

    )