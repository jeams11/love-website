from datetime import datetime
from zoneinfo import ZoneInfo


def get_beijing_time():

    return datetime.now(
        ZoneInfo("Asia/Shanghai")
    )



def check_sleep_time():

    now=get_beijing_time()

    hour=now.hour


    if 0 <= hour < 6:

        return True


    return False



def sleep_message(username,time_text):

    return (
        f"🌙 夜晚小提醒\n\n"
        f"{username}刚刚在 "
        f"{time_text} 打开了我们的空间。\n\n"
        f"可能还没有休息，"
        f"记得关心一下对方哦 ❤️\n\n"
        f"AI根据访问时间生成，"
        f"结果可能存在偏差。"
    )