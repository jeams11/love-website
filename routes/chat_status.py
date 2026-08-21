from flask import session
from extensions import socketio
from flask_socketio import emit

from database import read_messages


# ==========================
# 正在输入
# ==========================

@socketio.on("typing")
def user_typing():

    username = session.get(
        "user"
    )

    if not username:
        return


    emit(
        "user_typing",
        {
            "user": username,
            "typing": True
        },
        broadcast=True
    )


@socketio.on("stop_typing")
def stop_typing():

    username = session.get(
        "user"
    )

    if not username:
        return


    emit(
        "user_typing",
        {
            "user": username,
            "typing": False
        },
        broadcast=True
    )


# ==========================
# 已读
# ==========================

@socketio.on("read_message")
def read_message_event(data):

    username = session.get(
        "user"
    )

    if not username:
        return


    message_id = data.get(
        "id"
    )


    read_messages(
        username
    )


    emit(
        "message_read",
        {
            "id": message_id,
            "user": username
        },
        broadcast=True
    )