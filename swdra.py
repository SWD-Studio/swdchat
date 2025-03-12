# -*- encoding=utf-8 -*-
#    Copyright (C) 2020-2025  SWD Studio

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#     any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#    You can contact us on <http://swdstudio.github.com>.

# 20250309
# 处理不存在baiduaip.json的情况

import wave
from pyaudio import PyAudio, paInt16
from aip import AipSpeech
from threading import Thread
from types import FunctionType
from json import load
from tkinter.messagebox import showerror

NUM_SAMPLES = 2000
flag = False  # 继续录?


def asr_result_function(res): return print(res)

err=None

try:
    fp=open('baiduaip.json')
    aipdict=load(fp)
    BaiduAPP_ID = aipdict['BaiduAPP_ID']
    BaiduAPI_KEY = aipdict['BaiduAPI_KEY']
    SECRET_KEY = aipdict['SECRET_KEY']
    client = AipSpeech(BaiduAPP_ID, BaiduAPI_KEY, SECRET_KEY)
except Exception as e:
    err=e

# 保存录音文件

def save_wave_file(filename, data):
    wf = wave.open(filename, 'wb')  # 打开WAV文档
    wf.setnchannels(1)  # 配置声道数
    wf.setsampwidth(2)  # 配置量化位数
    wf.setframerate(16000)  # 采样频率
    wf.writeframes(b"".join(data))  # 将wav_data转换为二进制数据写入文件
    wf.close()

# 定义开始录音函数


def start_recording_process():
    th = Thread(target=recording_process, daemon=True)
    th.start()


def recording_process():
    global flag
    if err is None:
        pa = PyAudio()
        flag = True
        stream = pa.open(format=paInt16,
                         channels=1,
                         rate=16000,
                         input=True,
                         frames_per_buffer=NUM_SAMPLES)
        audioBuffer = []   # 录音缓存数组
        # 循环采集音频
        while flag:
            string_audio_data = stream.read(NUM_SAMPLES)
            audioBuffer.append(string_audio_data)
        save_wave_file('./audio.wav', audioBuffer)
        stream.close()
        result = asr_updata()
        val = 'result' in result.keys()
    else:
        global finish_recording_process
        finish_recording_process = lambda:asr_result_function(res_dict)
        val=0
        result = {'err_msg':'%s %s'%(type(err),err)}
    res_dict = {'asr_error_state_code': int(not val)}
    if val:
        res_dict['asr_result_message'] = result["result"][0]
    else:
        res_dict['asr_error_infomation'] = result["err_msg"]
    asr_result_function(res_dict)

# 定义完成录音函数


def finish_recording_process():
    global flag
    flag = False

# 语音识别函数


def asr_updata():
    with open('./audio.wav', 'rb') as f:
        audio_data = f.read()
    result = client.asr(audio_data,
                        'wav', 16000, {
                            'dev_pid': 1537,
                        })
    print(result)
    val = 'result' in result.keys()
    print("val:", val)
    # if val == True:
    #     result_text = result["result"][0]
    # else:
    #     result_text = '语音识别错误'
    return result


def asr_result(func: FunctionType):
    global asr_result_function
    asr_result_function = func
    return func


if __name__ == '__main__':
    input('start')
    start_recording_process()
    input('finish')
    print(finish_recording_process())
