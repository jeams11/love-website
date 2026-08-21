from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)


from extensions import bcrypt


from database import (
    get_user,
    update_status,
    add_login_log,
    add_visit
)



auth_bp = Blueprint(
    "auth",
    __name__
)



@auth_bp.route(
    "/",
    methods=["GET","POST"]
)

@auth_bp.route(
    "/login",
    methods=["GET","POST"]
)

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
                url_for(
                    "home.home"
                )
            )


    return render_template(
        "login.html"
    )
# ==========================
# 退出登录
# ==========================

@auth_bp.route("/logout")
def logout():

    username=session.get("user")

    if username:
        update_status(
            username,
            0
        )


    session.clear()


    return redirect(
        url_for(
            "auth.login"
        )
    )