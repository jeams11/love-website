import sqlite3
import os
from datetime import datetime


DB_PATH = "data/love.db"



# ==========================
# 数据库连接
# ==========================

def get_db():

    os.makedirs(
        "data",
        exist_ok=True
    )


    conn = sqlite3.connect(
        DB_PATH
    )


    conn.row_factory = sqlite3.Row


    return conn






# ==========================
# 初始化数据库
# ==========================

def init_db():


    conn = get_db()

    cursor = conn.cursor()



    # 用户

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        password TEXT,

        created TEXT

    )
    """)



    # 在线状态

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS status(

        username TEXT UNIQUE,

        online INTEGER DEFAULT 0,

        last_time REAL

    )
    """)




    # 登录记录

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_logs(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        ip TEXT,

        user_agent TEXT,

        time TEXT

    )
    """)




    # 设备

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        device_name TEXT,

        device_id TEXT,

        last_time TEXT

    )
    """)




    # 网站访问

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visits(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        ip TEXT,

        time TEXT

    )
    """)



    conn.commit()

    conn.close()







# ==========================
# 用户
# ==========================


def add_user(username,password):


    conn=get_db()

    cursor=conn.cursor()



    cursor.execute(

        """

        INSERT OR IGNORE INTO users

        (username,password,created)

        VALUES(?,?,?)

        """,

        (

            username,

            password,

            datetime.now().strftime(
                "%Y-%m-%d"
            )

        )

    )



    cursor.execute(

        """

        INSERT OR IGNORE INTO status

        (username,online,last_time)

        VALUES(?,?,?)

        """,

        (

            username,

            0,

            0

        )

    )



    conn.commit()

    conn.close()





def get_user(username):


    conn=get_db()

    cursor=conn.cursor()



    result=cursor.execute(

        """

        SELECT *

        FROM users

        WHERE username=?

        """,

        (username,)

    ).fetchone()



    conn.close()


    return result







# ==========================
# 状态
# ==========================


def update_status(username,online):


    conn=get_db()

    cursor=conn.cursor()



    cursor.execute(

        """

        UPDATE status

        SET online=?,

        last_time=?

        WHERE username=?

        """,

        (

            online,

            datetime.now().timestamp(),

            username

        )

    )



    conn.commit()

    conn.close()





def get_status(username):


    conn=get_db()

    cursor=conn.cursor()



    result=cursor.execute(

        """

        SELECT *

        FROM status

        WHERE username=?

        """,

        (username,)

    ).fetchone()



    conn.close()


    return result







# ==========================
# 登录日志
# ==========================


def add_login_log(username,ip,user_agent):


    conn=get_db()

    cursor=conn.cursor()



    cursor.execute(

        """

        INSERT INTO login_logs

        (username,ip,user_agent,time)

        VALUES(?,?,?,?)

        """,

        (

            username,

            ip,

            user_agent,

            datetime.now().strftime(

                "%Y-%m-%d %H:%M:%S"

            )

        )

    )


    conn.commit()

    conn.close()






def get_login_logs():


    conn=get_db()

    cursor=conn.cursor()



    result=cursor.execute(

        """

        SELECT *

        FROM login_logs

        ORDER BY id DESC

        LIMIT 20

        """

    ).fetchall()



    conn.close()


    return result







# ==========================
# 设备记录
# ==========================


def add_device(username,device_name,device_id):


    conn=get_db()

    cursor=conn.cursor()



    cursor.execute(

        """

        INSERT INTO devices

        (username,device_name,device_id,last_time)

        VALUES(?,?,?,?)

        """,

        (

            username,

            device_name,

            device_id,

            datetime.now().strftime(

                "%Y-%m-%d %H:%M:%S"

            )

        )

    )



    conn.commit()

    conn.close()






def get_devices():


    conn=get_db()

    cursor=conn.cursor()



    result=cursor.execute(

        """

        SELECT *

        FROM devices

        ORDER BY id DESC

        LIMIT 20

        """

    ).fetchall()



    conn.close()


    return result







# ==========================
# 网站访问
# ==========================


def add_visit(ip):


    conn=get_db()

    cursor=conn.cursor()



    cursor.execute(

        """

        INSERT INTO visits

        (ip,time)

        VALUES(?,?)

        """,

        (

            ip,

            datetime.now().strftime(

                "%Y-%m-%d %H:%M:%S"

            )

        )

    )



    conn.commit()

    conn.close()







def get_visit_count():


    conn=get_db()

    cursor=conn.cursor()



    result=cursor.execute(

        """

        SELECT COUNT(*)

        FROM visits

        """

    ).fetchone()[0]



    conn.close()


    return result







def get_today_visit_count():


    conn=get_db()

    cursor=conn.cursor()



    today=datetime.now().strftime(

        "%Y-%m-%d"

    )



    result=cursor.execute(

        """

        SELECT COUNT(*)

        FROM visits

        WHERE time LIKE ?

        """,

        (

            today+"%",

        )

    ).fetchone()[0]



    conn.close()


    return result