import re


# 常见情侣语音纠错

replace_words={

    "包包":"宝宝",

    "爸爸":"宝宝",

    "抱抱":"宝宝",

    "宝宝":"宝宝",

    "贝贝":"宝贝",

    "宝贝":"宝贝",

    "包贝":"宝贝",

}



def correct_voice_text(text):


    if not text:

        return ""



    result=text



    for a,b in replace_words.items():

        result=result.replace(
            a,
            b
        )



    # 常见句式恢复

    if (
        "在干嘛" in result
        and
        "宝宝" not in result
        and
        "宝贝" not in result
    ):

        pass



    # 标点优化

    result=result.strip()


    if result.endswith("?")==False:

        if "吗" in result:

            result+="?"



    return result