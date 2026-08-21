import sqlite3
from datetime import datetime
import time
import os
import json


DB_PATH = "data/love.db"


MAX_UPLOAD_SIZE = 50 * 1024 * 1024



# ==========================
# 数据库连接
# ==========================

def get_db():

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn



# ==========================
# 时间
# ==========================

def now_time():

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )



# ==========================
# 初始化数据库
# ==========================

def init_db():

    os.makedirs(
        "data",
        exist_ok=True
    )


    conn = get_db()

    cursor = conn.cursor()



    # ==========================
    # 用户
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT UNIQUE,

        password TEXT

    )
    """)



    # ==========================
    # 在线状态
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS status(

        username TEXT PRIMARY KEY,

        online INTEGER DEFAULT 0,

        last_time REAL

    )
    """)



    # ==========================
    # 登录日志
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_logs(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        ip TEXT,

        user_agent TEXT,

        time TEXT

    )
    """)



    # ==========================
    # 设备
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        device_name TEXT,

        device_id TEXT,

        last_time TEXT

    )
    """)



    # ==========================
    # 访问统计
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visits(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        ip TEXT,

        time TEXT

    )
    """)



    # ==========================
    # 聊天消息
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        sender TEXT,

        receiver TEXT,

        content TEXT,

        type TEXT DEFAULT 'text',

        voice_text TEXT DEFAULT '',

        created TEXT,

        read_status INTEGER DEFAULT 0,

        withdrawn INTEGER DEFAULT 0,

        withdraw_time TEXT DEFAULT '',

        quote_id INTEGER DEFAULT 0,

        quote_text TEXT DEFAULT '',

        deleted_by TEXT DEFAULT '',

        delivery_status INTEGER DEFAULT 0

    )
    """)



    # ==========================
    # 用户资料
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



    # ==========================
    # AI 夜间访问
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS night_visits(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        visit_time REAL,

        beijing_time TEXT,

        is_night INTEGER DEFAULT 0

    )
    """)



    # ==========================
    # AI提醒
    # ==========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_notifications(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT,

        target_user TEXT,

        content TEXT,

        created_time REAL,

        read_status INTEGER DEFAULT 0

    )
    """)



    conn.commit()



    # ==========================
    # 老数据库兼容
    # ==========================


    columns = [

        "withdrawn INTEGER DEFAULT 0",

        "withdraw_time TEXT DEFAULT ''",

        "quote_id INTEGER DEFAULT 0",

        "quote_text TEXT DEFAULT ''",

        "deleted_by TEXT DEFAULT ''",

        "voice_text TEXT DEFAULT ''",

        "delivery_status INTEGER DEFAULT 0"

    ]


    for column in columns:

        try:

            cursor.execute(

                f"""

                ALTER TABLE messages

                ADD COLUMN {column}

                """

            )

        except sqlite3.OperationalError:

            pass



    # ==========================
    # 索引优化
    # ==========================


    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_messages_users

    ON messages(sender,receiver)

    """)



    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_messages_receiver_read

    ON messages(receiver,read_status)

    """)



    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS idx_device_id

    ON devices(device_id)

    """)



    conn.commit()

    conn.close()
# ==========================
# 用户
# ==========================

def add_user(username, password):

    conn = get_db()

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

    conn = get_db()

    user = conn.execute(
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
# 个人资料
# ==========================

def create_profile(username):

    conn = get_db()

    conn.execute(
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
            now_time()
        )
    )

    conn.commit()
    conn.close()



def get_profile(username):

    conn = get_db()

    profile = conn.execute(
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

    conn = get_db()

    conn.execute(
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



def update_avatar(username, avatar):

    conn = get_db()

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
# 在线状态
# ==========================

def update_status(username, online):

    conn = get_db()

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

    conn = get_db()

    status = conn.execute(
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

    return status



# ==========================
# 登录日志
# ==========================

def add_login_log(
    username,
    ip,
    user_agent
):

    conn = get_db()

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
            now_time()
        )
    )

    conn.commit()
    conn.close()



def get_login_logs():

    conn = get_db()

    logs = conn.execute(
        """
        SELECT *

        FROM login_logs

        ORDER BY id DESC

        """
    ).fetchall()

    conn.close()

    return logs



# ==========================
# 设备
# ==========================

def add_device(
    username,
    name,
    device_id
):

    conn = get_db()

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
            now_time()
        )
    )

    conn.commit()
    conn.close()



def get_devices():

    conn = get_db()

    devices = conn.execute(
        """
        SELECT *

        FROM devices

        ORDER BY id DESC

        """
    ).fetchall()

    conn.close()

    return devices



# ==========================
# 访问统计
# ==========================

def add_visit(ip):

    conn = get_db()

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
            now_time()
        )
    )

    conn.commit()
    conn.close()



def get_visit_count():

    conn = get_db()

    count = conn.execute(
        """
        SELECT COUNT(*)

        FROM visits

        """
    ).fetchone()[0]

    conn.close()

    return count



def get_today_visit_count():

    conn = get_db()

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    count = conn.execute(
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

def add_message(
    sender,
    receiver,
    content,
    msg_type="text",
    quote_id=0,
    quote_text="",
    voice_text=""
):

    conn = get_db()

    cursor = conn.execute(
        """
        INSERT INTO messages
        (
            sender,
            receiver,
            content,
            type,
            voice_text,
            created,
            read_status,
            withdrawn,
            withdraw_time,
            quote_id,
            quote_text,
            deleted_by,
            delivery_status
        )

        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            sender,
            receiver,
            content,
            msg_type,
            voice_text,
            now_time(),
            0,
            0,
            "",
            quote_id,
            quote_text,
            "",
            0
        )
    )

    message_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return message_id



def add_image_message(
    sender,
    receiver,
    filename
):

    return add_message(
        sender,
        receiver,
        filename,
        "image"
    )



def add_file_message(
    sender,
    receiver,
    filename
):

    return add_message(
        sender,
        receiver,
        filename,
        "file"
    )



def add_voice_message(
    sender,
    receiver,
    filename,
    voice_text=""
):

    return add_message(
        sender,
        receiver,
        filename,
        "voice",
        0,
        "",
        voice_text
    )



# ==========================
# 获取聊天记录
# ==========================

def get_messages(
    user1,
    user2
):

    conn = get_db()

    messages = conn.execute(
        """
        SELECT *

        FROM messages

        WHERE

        (
            sender=?
            AND
            receiver=?
        )

        OR

        (
            sender=?
            AND
            receiver=?
        )

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

    return messages



# ==========================
# 获取单条消息
# ==========================

def get_message(message_id):

    conn = get_db()

    message = conn.execute(
        """
        SELECT *

        FROM messages

        WHERE id=?

        """,
        (
            message_id,
        )
    ).fetchone()


    conn.close()

    return message



# ==========================
# 撤回消息
# ==========================

def withdraw_message(message_id):

    conn = get_db()

    conn.execute(
        """
        UPDATE messages

        SET

        withdrawn=1,

        withdraw_time=?

        WHERE id=?

        """,
        (
            now_time(),
            message_id
        )
    )

    conn.commit()
    conn.close()



# ==========================
# 删除消息
# ==========================

def delete_message_for_user(
    message_id,
    username
):

    conn = get_db()


    msg = conn.execute(
        """
        SELECT deleted_by

        FROM messages

        WHERE id=?

        """,
        (
            message_id,
        )
    ).fetchone()



    users = []


    if msg and msg["deleted_by"]:

        try:

            users = json.loads(
                msg["deleted_by"]
            )

        except:

            users = []



    if username not in users:

        users.append(
            username
        )



    conn.execute(
        """
        UPDATE messages

        SET deleted_by=?

        WHERE id=?

        """,
        (
            json.dumps(
                users,
                ensure_ascii=False
            ),
            message_id
        )
    )


    conn.commit()
    conn.close()



# ==========================
# 已读
# ==========================

def read_messages(user):

    conn = get_db()

    conn.execute(
        """
        UPDATE messages

        SET read_status=1

        WHERE receiver=?

        """,
        (
            user,
        )
    )


    conn.commit()
    conn.close()



# ==========================
# 未读数量
# ==========================

def get_unread_count(user):

    conn = get_db()


    count = conn.execute(
        """
        SELECT COUNT(*)

        FROM messages

        WHERE

        receiver=?

        AND

        read_status=0

        """,
        (
            user,
        )
    ).fetchone()[0]


    conn.close()


    return count



# ==========================
# 消息统计
# ==========================

def get_message_count():

    conn = get_db()


    count = conn.execute(
        """
        SELECT COUNT(*)

        FROM messages

        """
    ).fetchone()[0]


    conn.close()


    return count



def get_today_message_count():

    conn = get_db()


    today = datetime.now().strftime(
        "%Y-%m-%d"
    )


    count = conn.execute(
        """
        SELECT COUNT(*)

        FROM messages

        WHERE created LIKE ?

        """,
        (
            today+"%",
        )
    ).fetchone()[0]


    conn.close()


    return count

# ==========================
# AI 夜间访问记录
# ==========================

def add_night_visit(
    username,
    is_night
):

    conn = get_db()

    conn.execute(
        """
        INSERT INTO night_visits
        (
            username,
            visit_time,
            beijing_time,
            is_night
        )

        VALUES(?,?,?,?)

        """,
        (
            username,
            time.time(),
            now_time(),
            is_night
        )
    )

    conn.commit()
    conn.close()



def get_night_visits(
    username=None
):

    conn = get_db()


    if username:

        data = conn.execute(
            """
            SELECT *

            FROM night_visits

            WHERE username=?

            ORDER BY id DESC

            """,
            (
                username,
            )
        ).fetchall()


    else:

        data = conn.execute(
            """
            SELECT *

            FROM night_visits

            ORDER BY id DESC

            """
        ).fetchall()



    conn.close()


    return data



# ==========================
# AI提醒
# ==========================

def add_ai_notification(
    username,
    target_user,
    content
):

    conn = get_db()


    conn.execute(
        """
        INSERT INTO ai_notifications
        (
            username,
            target_user,
            content,
            created_time,
            read_status
        )

        VALUES(?,?,?,?,?)

        """,
        (
            username,
            target_user,
            content,
            time.time(),
            0
        )
    )


    conn.commit()

    conn.close()



def get_ai_notifications(
    username
):

    conn = get_db()


    data = conn.execute(
        """
        SELECT *

        FROM ai_notifications

        WHERE target_user=?

        ORDER BY id DESC

        """,
        (
            username,
        )
    ).fetchall()



    conn.close()


    return data



def read_ai_notifications(
    username
):

    conn = get_db()


    conn.execute(
        """
        UPDATE ai_notifications

        SET read_status=1

        WHERE target_user=?

        """,
        (
            username,
        )
    )


    conn.commit()

    conn.close()



# ==========================
# AI提醒未读数量
# ==========================

def get_ai_notification_count(
    username
):

    conn = get_db()


    count = conn.execute(
        """
        SELECT COUNT(*)

        FROM ai_notifications

        WHERE

        target_user=?

        AND

        read_status=0

        """,
        (
            username,
        )
    ).fetchone()[0]


    conn.close()


    return count



# ==========================
# 初始化检查
# ==========================

if __name__ == "__main__":

    init_db()

    print(
        "数据库初始化完成"
    )