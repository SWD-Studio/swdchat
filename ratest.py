from time import sleep
from threading import Thread

def start_recording_process():
    print('start')

def finish_recording_proces():
    sleep(1.0)
    fun({'asr_error_state_code':1,'asr_result_message':'haha','asr_error_infomation':'!!!'})
    print('end')
def asr_result(func):
    global fun
    fun=func
    return func
def finish_recording_process():
    aa=Thread(target=finish_recording_proces,daemon=True)
    aa.start()