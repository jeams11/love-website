from flask import (
    Blueprint,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

from functools import wraps

from database import (
    get_messages,
    add_voice_message
)

from voice import speech_to_text

from voice_context_ai import correct_with_context

import os
import time




voice_bp = Blueprint(
    "voice",
    __name__
)






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






def get_other_user(username):

    return (
        "真真"
        if username=="泽泽"
        else
        "泽泽"
    )







# ==========================
# 语音上传
# Whisper + AI理解
# ==========================

@voice_bp.route(
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

            "success":False,

            "error":"no voice"

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





    whisper_text=""


    ai_text=""




    try:


        # ==========================
        # Whisper识别
        # ==========================

        whisper_text=speech_to_text(

            path

        )




        # ==========================
        # 获取聊天上下文
        # ==========================

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






        # ==========================
        # AI理解
        # ==========================

        ai_text=correct_with_context(

            whisper_text,

            history

        )




    except Exception as e:


        print(

            "语音AI处理失败:",

            e

        )


        ai_text=whisper_text




    # ==========================
    # 保存语音消息
    # ==========================

    add_voice_message(

        sender,

        receiver,

        filename,

        ai_text

    )




    return jsonify({

        "success":True,

        "text":ai_text,

        "raw_text":whisper_text,

        "emotion":None

    })