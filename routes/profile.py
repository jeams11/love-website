from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from functools import wraps

from database import (
    get_profile,
    update_profile,
    update_avatar
)

import os
import time



profile_bp = Blueprint(
    "profile",
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







# ==========================
# 个人资料
# ==========================

@profile_bp.route(
    "/profile",
    methods=["GET","POST"]
)

@login_required

def profile():


    username=session["user"]



    if request.method=="POST":


        nickname=request.form.get(
            "nickname",
            ""
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

            url_for(
                "profile.profile"
            )

        )






    return render_template(

        "profile.html",

        profile=get_profile(

            username

        )

    )

