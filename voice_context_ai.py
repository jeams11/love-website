import requests
import json
import os
import re
import time


# ==========================
# Ollama配置
# ==========================

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "qwen2.5:7b"


# ==========================
# 记忆文件
# ==========================

MEMORY_FILE = "voice_memory.json"



# ==========================
# 默认记忆
# ==========================

DEFAULT_MEMORY = {

    "replace": {

        "包包": "宝宝"

    },

    "protect": [

        "泽泽",

        "真真",

        "宝宝"

    ]

}





# ==========================
# Memory读取
# ==========================

def load_memory():

    if not os.path.exists(
        MEMORY_FILE
    ):

        save_memory(
            DEFAULT_MEMORY
        )

        return DEFAULT_MEMORY



    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)



    except:

        return DEFAULT_MEMORY






def save_memory(data):

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )


    except:

        pass






# ==========================
# 本地快速修正
# ==========================

def local_replace(text):


    memory=load_memory()


    replace=memory.get(
        "replace",
        {}
    )


    for wrong,right in replace.items():

        text=text.replace(
            wrong,
            right
        )


    return text






# ==========================
# 保护词
# ==========================

def protect_text(text):

    memory=load_memory()


    words=memory.get(
        "protect",
        []
    )


    for word in words:

        text=text.replace(
            word,
            f"<{word}>"
        )


    return text




def restore_text(text):

    return text.replace(
        "<",
        ""
    ).replace(
        ">",
        ""
    )





# ==========================
# 上下文整理
# ==========================

def build_context(history):


    if not history:

        return "暂无聊天记录"



    lines=history.split(
        "\n"
    )


    return "\n".join(
        lines[-20:]
    )






# ==========================
# AI请求
# ==========================

def ask_qwen(
    text,
    history
):


    protected=protect_text(
        text
    )


    context=build_context(
        history
    )


    prompt=f"""
你是微信语音识别纠错系统。

你的工作：
根据聊天上下文，判断语音识别是否有错误。


重要规则：

1. 保留用户原本说话方式。
2. 不进行语言润色。
3. 不改变句子结构。
4. 不添加语气词。
5. 不删除原来的语气词。
6. 只修正高概率错误。
7. 优先判断昵称、人名、专属称呼。
8. 如果无法确定，保持原文。
9. 不输出解释。
10. 不输出聊天记录。


例子：

聊天：
泽泽：辛苦啦宝宝

输入：
包包在干嘛呢

输出：
宝宝在干嘛呢


聊天：
泽泽：刚吃饭

输入：
我把这个拿了

输出：
我把这个拿了


聊天记录：

{context}


当前语音：

{protected}


只输出最终文字：
"""


    try:

        r=requests.post(

            OLLAMA_URL,

            json={

                "model":MODEL,

                "prompt":prompt,

                "stream":False,

                "options":{

                    "temperature":0,

                    "top_p":0.1,

                    "num_predict":50

                }

            },

            timeout=60

        )


        data=r.json()


        return data.get(
            "response",
            ""
        ).strip()



    except Exception as e:

        print(
            "Qwen Error:",
            e
        )

        return ""







# ==========================
# AI输出清理
# ==========================

def clean_result(
    result,
    original
):


    if not result:

        return original



    result=result.strip()



    # 删除AI废话

    remove=[

        "最终文字:",

        "结果:",

        "答案:"

    ]


    for x in remove:

        result=result.replace(
            x,
            ""
        )



    result=result.strip()



    # 删除聊天格式

    lines=result.split(
        "\n"
    )


    output=[]


    for line in lines:


        if re.match(
            r"^(泽泽|真真).*[:：]",
            line
        ):

            continue


        output.append(
            line
        )


    result="\n".join(
        output
    ).strip()



    result=restore_text(
        result
    )



    # 防止AI扩写

    if len(result) > len(original)+15:

        return original



    if not result:

        return original



    return result






# ==========================
# 主函数
# ==========================

def correct_with_context(
    text,
    history=""
):


    if not text:

        return ""



    start=time.time()



    # 第一层：
    # 本地记忆

    original=text


    text=local_replace(
        text
    )



    # 第二层：
    # AI判断

    result=ask_qwen(
        text,
        history
    )



    # 第三层：
    # 安全过滤

    result=clean_result(
        result,
        text
    )


    cost=round(
        time.time()-start,
        2
    )


    print(
        f"语音AI纠错耗时:{cost}s"
    )


    return result