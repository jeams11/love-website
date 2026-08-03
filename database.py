import sqlite3
from datetime import datetime
import time


DB_PATH = "data/love.db"


def get_db():

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


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        password TEXT

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS status(

        username TEXT PRIMARY KEY,

        online INTEGER,

        last_time REAL

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_logs(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        ip TEXT,

        user_agent TEXT,

        time TEXT

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        device_name TEXT,

        device_id TEXT,

        last_time TEXT

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visits(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        ip TEXT,

        time TEXT

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        sender TEXT,

        receiver TEXT,

        content TEXT,

        type TEXT DEFAULT 'text',

        created TEXT,

        read_status INTEGER DEFAULT 0

    )
    """)


    # ==========================
    # 个人资料
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiles(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        nickname TEXT,

        avatar TEXT DEFAULT 'default.png',

        birthday_type TEXT DEFAULT 'solar',

        birthday TEXT,

        lunar_month TEXT,

        lunar_day TEXT,

        lunar_solar_date TEXT,

        signature TEXT,

        created TEXT

    )
    """)


    conn.commit()

    conn.close()



# ==========================
# 用户
# ==========================

def add_user(username,password):

    conn=get_db()

    conn.execute(
        """
        INSERT OR IGNORE INTO users
        (
            username,
            password
        )

        VALUES(?,?)

        """,
        (
            username,
            password
        )
    )

    conn.commit()

    conn.close()



def get_user(username):

    conn=get_db()

    user=conn.execute(
        """
        SELECT *

        FROM users

        WHERE username=?

        """,
        (
            username,
        )
    ).fetchone()

    conn.close()

    return user



# ==========================
# 个人资料系统
# ==========================

def create_profile(username):

    conn=get_db()

    cursor=conn.cursor()


    cursor.execute(
        """
        INSERT OR IGNORE INTO profiles

        (
            username,
            nickname,
            avatar,
            birthday_type,
            birthday,
            lunar_month,
            lunar_day,
            lunar_solar_date,
            signature,
            created
        )

        VALUES(?,?,?,?,?,?,?,?,?,?)

        """,

        (
            username,
            username,
            "default.png",
            "solar",
            "",
            "",
            "",
            "",
            "",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )


    conn.commit()

    conn.close()



def get_profile(username):

    conn=get_db()


    profile=conn.execute(
        """
        SELECT *

        FROM profiles

        WHERE username=?

        """,
        (
            username,
        )

    ).fetchone()


    conn.close()

    return profile



def update_profile(
    username,
    nickname,
    birthday_type,
    birthday,
    lunar_month,
    lunar_day,
    lunar_solar_date,
    signature
):

    conn=get_db()

    cursor=conn.cursor()


    cursor.execute(
        """
        UPDATE profiles

        SET

        nickname=?,

        birthday_type=?,

        birthday=?,

        lunar_month=?,

        lunar_day=?,

        lunar_solar_date=?,

        signature=?

        WHERE username=?

        """,

        (
            nickname,
            birthday_type,
            birthday,
            lunar_month,
            lunar_day,
            lunar_solar_date,
            signature,
            username
        )
    )


    conn.commit()

    conn.close()



def update_avatar(username,avatar):

    conn=get_db()

    conn.execute(
        """
        UPDATE profiles

        SET avatar=?

        WHERE username=?

        """,
        (
            avatar,
            username
        )
    )

    conn.commit()

    conn.close()
# ==========================
# 状态
# ==========================

def update_status(username,online):

    conn=get_db()

    conn.execute(
        """
        INSERT OR REPLACE INTO status

        (
            username,
            online,
            last_time
        )

        VALUES(?,?,?)

        """,
        (
            username,
            online,
            time.time()
        )
    )

    conn.commit()

    conn.close()



def get_status(username):

    conn=get_db()

    data=conn.execute(
        """
        SELECT *

        FROM status

        WHERE username=?

        """,
        (
            username,
        )
    ).fetchone()

    conn.close()

    return data



# ==========================
# 登录日志
# ==========================

def add_login_log(username,ip,user_agent):

    conn=get_db()

    conn.execute(
        """
        INSERT INTO login_logs

        (
            username,
            ip,
            user_agent,
            time
        )

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

    data=conn.execute(
        """
        SELECT *

        FROM login_logs

        ORDER BY id DESC

        """
    ).fetchall()

    conn.close()

    return data



# ==========================
# 设备
# ==========================

def add_device(username,name,device_id):

    conn=get_db()

    conn.execute(
        """
        INSERT INTO devices

        (
            username,
            device_name,
            device_id,
            last_time
        )

        VALUES(?,?,?,?)

        """,
        (
            username,
            name,
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

    data=conn.execute(
        """
        SELECT *

        FROM devices

        ORDER BY id DESC

        """
    ).fetchall()

    conn.close()

    return data



# ==========================
# 访问统计
# ==========================

def add_visit(ip):

    conn=get_db()

    conn.execute(
        """
        INSERT INTO visits

        (
            ip,
            time
        )

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

    count=conn.execute(
        """
        SELECT COUNT(*)

        FROM visits

        """
    ).fetchone()[0]

    conn.close()

    return count



def get_today_visit_count():

    conn=get_db()

    today=datetime.now().strftime(
        "%Y-%m-%d"
    )

    count=conn.execute(
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

    return count



# ==========================
# 聊天系统
# ==========================

def add_message(sender,receiver,content):

    conn=get_db()

    conn.execute(
        """
        INSERT INTO messages

        (
            sender,
            receiver,
            content,
            type,
            created,
            read_status
        )

        VALUES(?,?,?,?,?,?)

        """,
        (
            sender,
            receiver,
            content,
            "text",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            0
        )
    )

    conn.commit()

    conn.close()



def add_image_message(sender,receiver,filename):

    conn=get_db()

    conn.execute(
        """
        INSERT INTO messages

        (
            sender,
            receiver,
            content,
            type,
            created,
            read_status
        )

        VALUES(?,?,?,?,?,?)

        """,
        (
            sender,
            receiver,
            filename,
            "image",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            0
        )
    )

    conn.commit()

    conn.close()



def get_messages(user1,user2):

    conn=get_db()

    data=conn.execute(
        """
        SELECT *

        FROM messages

        WHERE

        (sender=? AND receiver=?)

        OR

        (sender=? AND receiver=?)

        ORDER BY id ASC

        """,
        (
            user1,
            user2,
            user2,
            user1
        )
    ).fetchall()

    conn.close()

    return data



def get_unread_count(user):

    conn=get_db()

    count=conn.execute(
        """
        SELECT COUNT(*)

        FROM messages

        WHERE receiver=?

        AND read_status=0

        """,
        (
            user,
        )
    ).fetchone()[0]

    conn.close()

    return count