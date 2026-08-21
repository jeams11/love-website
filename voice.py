from faster_whisper import WhisperModel
from opencc import OpenCC

import subprocess
import os
import uuid
import glob


# ==========================
# 自动寻找 Whisper 本地模型
# ==========================

def find_whisper_model():

    model_files = glob.glob(
        os.path.expanduser(
            "~/.cache/huggingface/hub/models--Systran--faster-whisper-medium/**/model.bin"
        ),
        recursive=True
    )


    if not model_files:

        raise FileNotFoundError(
            "没有找到 faster-whisper-medium 本地模型"
        )


    model_path = os.path.dirname(
        model_files[0]
    )


    print(
        "Whisper模型:",
        model_path
    )


    return model_path



MODEL_PATH = find_whisper_model()



# ==========================
# 加载模型
# ==========================

model = WhisperModel(

    MODEL_PATH,

    device="cpu",

    compute_type="int8"

)



# 繁体转简体

converter = OpenCC(
    "t2s"
)





# ==========================
# 音频转换
# ==========================

def convert_audio(input_file):

    output_file = (

        "/tmp/"

        +

        str(uuid.uuid4())

        +

        ".wav"

    )


    subprocess.run(

        [
            "ffmpeg",

            "-y",

            "-i",

            input_file,

            "-ar",

            "16000",

            "-ac",

            "1",

            "-vn",

            output_file
        ],

        stdout=subprocess.DEVNULL,

        stderr=subprocess.DEVNULL

    )


    return output_file






# ==========================
# 语音识别
# ==========================

def speech_to_text(audio_path):

    wav_path=None


    try:


        wav_path = convert_audio(
            audio_path
        )



        segments, info = model.transcribe(

            wav_path,

            language="zh",

            beam_size=5,

            best_of=3,

            vad_filter=True,

            temperature=0,

            condition_on_previous_text=False

        )



        text=""


        for segment in segments:

            text += segment.text




        text = converter.convert(
            text
        )



        return text.strip()



    except Exception as e:


        print(
            "Whisper错误:",
            e
        )


        return ""



    finally:


        if wav_path and os.path.exists(wav_path):

            os.remove(
                wav_path
            )