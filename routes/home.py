from flask import (
    Blueprint,
    render_template,
    jsonify,
    session,
    redirect,
    url_for
)

from functools import wraps
from datetime import datetime
import time


from database import (
    get_db,
    get_status,
    update_status,
    get_profile
)



home_bp = Blueprint(
    "home",
    __name__
)



LOVE_START = datetime(
    2026,
    6,
    5
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
        if username == "泽泽"
        else
        "泽泽"
    )





def format_time(timestamp):

    if not timestamp:

        return "暂无记录"



    diff = time.time() - timestamp



    if diff < 60:

        return "刚刚"



    if diff < 3600:

        return f"{int(diff / 60)}分钟前"



    if diff < 86400:

        return f"{int(diff / 3600)}小时前"



    return datetime.fromtimestamp(

        timestamp

    ).strftime(

        "%m月%d日 %H:%M"

    )






# ==========================
# 首页
# ==========================

@home_bp.route("/home")

@login_required

def home():

    username = session["user"]


    other = get_other_user(
        username
    )


    profile = get_profile(
        username
    )


    other_profile = get_profile(
        other
    )



    days = (

        datetime.now()

        -

        LOVE_START

    ).days




    conn = get_db()


    memories = conn.execute(

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

@home_bp.route("/status")

@login_required

def status():


    other = get_other_user(

        session["user"]

    )


    data = get_status(
        other
    )


    online = False

    last = 0



    if data:


        last = data["last_time"]



        if (

            data["online"] == 1

            and

            time.time() - last <= 30

        ):

            online = True




    return jsonify({

        "online": online,

        "text":

        "在线"

        if online

        else

        "离线",


        "last":

        format_time(last)

    })







# ==========================
# 心跳
# ==========================

@home_bp.route("/heartbeat")

@login_required

def heartbeat():


    update_status(

        session["user"],

        1

    )


    return jsonify({

        "success": True

    })