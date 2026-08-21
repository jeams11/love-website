from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from functools import wraps

from datetime import datetime

import psutil
import platform


from database import (
    get_login_logs,
    get_devices,
    get_visit_count,
    get_today_visit_count
)


admin_bp = Blueprint(
    "admin",
    __name__
)



ADMIN_USERNAME="admin"

ADMIN_PASSWORD="101221"



system_history=[]





def admin_required(func):

    @wraps(func)

    def wrapper(*args, **kwargs):

        if not session.get("admin"):

            return redirect(
                url_for(
                    "admin.admin_login"
                )
            )


        return func(
            *args,
            **kwargs
        )


    return wrapper







# ==========================
# 管理登录
# ==========================

@admin_bp.route(
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
                    "admin.admin_dashboard"
                )

            )



    return render_template(
        "admin_login.html"
    )







# ==========================
# 管理首页
# ==========================

@admin_bp.route(
    "/admin/dashboard"
)

@admin_required

def admin_dashboard():


    return render_template(

        "admin.html",

        logs=get_login_logs(),

        devices=get_devices()

    )








# ==========================
# 系统状态
# ==========================

@admin_bp.route(
    "/admin/system"
)

@admin_required

def system_status():


    cpu=psutil.cpu_percent()



    system_history.append({

        "time":

        datetime.now().strftime(
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







# ==========================
# CPU历史
# ==========================

@admin_bp.route(
    "/admin/system/history"
)

@admin_required

def system_history_api():


    return jsonify(
        system_history
    )







# ==========================
# 网站统计
# ==========================

@admin_bp.route(
    "/admin/stats"
)

@admin_required

def admin_stats():


    return jsonify({

        "visits":

        get_visit_count(),


        "today":

        get_today_visit_count()

    })








# ==========================
# Tunnel状态
# ==========================

@admin_bp.route(
    "/admin/tunnel"
)

@admin_required

def admin_tunnel():


    return jsonify({

        "status":"running"

    })
