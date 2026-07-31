from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime
import time
import psutil
import platform
import subprocess

from database import (
    init_db,
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
    get_today_visit_count
)


app = Flask(__name__)

app.secret_key = "love-website-secret-key"

bcrypt = Bcrypt(app)


# ==========================
# 系统监控缓存
# ==========================

system_history = []


# ==========================
# 管理员账号
# ==========================

ADMIN_USERNAME = "admin"

ADMIN_PASSWORD = "101221"


# ==========================
# 初始化数据库
# ==========================

init_db()



# ==========================
# 默认用户
# ==========================

def create_default_users():

    users = {

        "泽泽": "110702",

        "真真": "110202"

    }


    for username, password in users.items():

        user = get_user(username)


        if not user:

            hashed = bcrypt.generate_password_hash(
                password
            ).decode("utf-8")


            add_user(
                username,
                hashed
            )



create_default_users()



# ==========================
# 用户权限
# ==========================

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user" not in session:

            return redirect(
                url_for("login")
            )


        return func(*args, **kwargs)


    return wrapper



def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("admin"):

            return redirect(
                url_for("admin_login")
            )


        return func(*args, **kwargs)


    return wrapper



# ==========================
# 时间格式
# ==========================

def format_time(timestamp):

    if not timestamp:

        return "暂无记录"


    diff = time.time() - timestamp


    if diff < 60:

        return "刚刚"


    elif diff < 3600:

        return f"{int(diff/60)}分钟前"


    elif diff < 86400:

        return f"{int(diff/3600)}小时前"


    return datetime.fromtimestamp(
        timestamp
    ).strftime(
        "%m月%d日 %H:%M"
    )



# ==========================
# 用户登录
# ==========================


@app.route("/", methods=["GET","POST"])
@app.route("/login", methods=["GET","POST"])

def login():

    add_visit(
        request.remote_addr
    )


    if request.method == "POST":


        username = request.form.get(
            "username"
        )


        password = request.form.get(
            "password"
        )


        user = get_user(username)



        if user and bcrypt.check_password_hash(

            user["password"],

            password

        ):


            session["user"] = username


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


            add_device(

                username,

                request.headers.get(
                    "User-Agent"
                )[:80],

                str(
                    hash(
                        request.headers.get(
                            "User-Agent"
                        )
                    )
                )

            )


            return redirect(
                url_for("home")
            )



    return render_template(
        "login.html"
    )



# ==========================
# 首页
# ==========================


@app.route("/home")

@login_required

def home():


    username = session["user"]


    other = (

        "真真"

        if username == "泽泽"

        else

        "泽泽"

    )


    return render_template(

        "home.html",

        user=username,

        other=other

    )
# ==========================
# 查看另一半状态
# ==========================


@app.route("/status")

@login_required

def status():


    username = session["user"]


    other = (

        "真真"

        if username == "泽泽"

        else

        "泽泽"

    )


    data = get_status(other)


    online = False

    last = 0


    if data:

        last = data["last_time"]


        if time.time() - last <= 10:

            online = True



    return jsonify({

        "online": online,

        "last": format_time(last)

    })




# ==========================
# 心跳
# ==========================


@app.route("/heartbeat")

@login_required

def heartbeat():


    username = session["user"]


    update_status(

        username,

        1

    )


    return jsonify({

        "success": True

    })





# ==========================
# 管理员登录
# ==========================


@app.route("/admin", methods=["GET","POST"])

def admin_login():


    # 已登录直接进入后台

    if session.get("admin"):

        return redirect(

            url_for(
                "admin_dashboard"
            )

        )



    if request.method == "POST":


        username = request.form.get(
            "username",
            ""
        )


        password = request.form.get(
            "password",
            ""
        )



        if (

            username == ADMIN_USERNAME

            and

            password == ADMIN_PASSWORD

        ):


            session["admin"] = True


            return redirect(

                url_for(
                    "admin_dashboard"
                )

            )



        return render_template(

            "admin_login.html",

            error="账号或密码错误"

        )



    return render_template(

        "admin_login.html"

    )






# ==========================
# 管理后台
# ==========================


@app.route("/admin/dashboard")

@admin_required

def admin_dashboard():


    logs = get_login_logs()


    devices = get_devices()



    return render_template(

        "admin.html",

        logs=logs,

        devices=devices

    )







# ==========================
# 系统监控
# ==========================


@app.route("/admin/system")

@admin_required

def system_status():


    cpu = psutil.cpu_percent()



    data = {


        "cpu": cpu,


        "memory":

            psutil.virtual_memory().percent,


        "disk":

            psutil.disk_usage("/").percent,


        "system":

            platform.system(),


        "machine":

            platform.machine()

    }



    system_history.append({

        "time":

            datetime.now().strftime(
                "%H:%M:%S"
            ),


        "cpu":

            cpu

    })



    if len(system_history) > 60:

        system_history.pop(0)



    return jsonify(data)






# ==========================
# CPU历史曲线
# ==========================


@app.route("/admin/system/history")

@admin_required

def system_history_api():


    return jsonify(

        system_history

    )





# ==========================
# Cloudflare Tunnel
# ==========================


@app.route("/admin/tunnel")

@admin_required

def tunnel_status():


    try:


        result = subprocess.check_output(

            [

                "cloudflared",

                "tunnel",

                "info"

            ],

            stderr=subprocess.STDOUT,

            timeout=5

        ).decode("utf-8")



        return jsonify({

            "online": True,

            "info": result[:300]

        })



    except Exception:


        return jsonify({

            "online": False,

            "info": "Tunnel Offline"

        })
    # ==========================
# 网站访问统计
# ==========================


@app.route("/admin/stats")

@admin_required

def admin_stats():


    return jsonify({

        "today":

            get_today_visit_count(),


        "total":

            get_visit_count()

    })






# ==========================
# 管理员退出
# ==========================


@app.route("/admin/logout")

def admin_logout():


    session.pop(

        "admin",

        None

    )


    return redirect(

        url_for(
            "admin_login"
        )

    )






# ==========================
# 用户退出
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

        url_for(
            "login"
        )

    )






# ==========================
# 启动
# ==========================


if __name__ == "__main__":


    app.run(

        host="0.0.0.0",

        port=9000

    )