#    Copyright (C) 2020-2024  SWD Code Group

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
#    You can contact us on swd-go.ys168.com.
#20240315
import swdlc as lc
from swdlc import getip
from sys import exit,stderr
from threading import Thread
from tkinter import *
from tkinter.filedialog  import *
from tkinter.scrolledtext import ScrolledText as ST
from tkinter.ttk import *
from tkinter.messagebox import showerror,showinfo
from time import sleep,localtime, strftime,time
from os.path import relpath
import filecmp
import os
class SchatBaseException(Exception):pass
class StopSending(SchatBaseException):pass
class ChatWindowError(SchatBaseException):pass
#{'username':用户名,'type':内容类型,'msg':内容,'addr':地址,'name':群组名,'chatid':群组id}
win_obj={}#已创建的对象
username=getip()
def gettime():
    t=strftime("%X", localtime())
    return t[:t.rfind(':')]
class Schat(object):
    enable_TLS=True
    message_color=('black','blue')
    enable_tips=True
    name=''#name of this Schat
    def __init__(self,address:tuple,**options):
        self._address=tuple(sorted(address))
        for i in options:
            exec('self.%s=%s'%(i,repr(options[i])))
        self._id=len(win_obj)
        self.chatid=time()
        win_obj[self.chatid]=self
    def _send(self,**kwargs):
        for ip,port in self._address:
            Thread(target=lc.send,
                   args=((kwargs,ip,str(port)))).start()
    def _sendimg(self):
        try:
            if (fp:=askopenfilename())=='':
                return
            open(fp).close()
            imgid=str(time())
            lc.share(imgid,fp,len(self._address))
        except Exception as e:
            showerror('SWDChat','找不到文件'+str(e))
            return
        self._send(username=username,
                   type='img',
                   imgname=fp.split('/')[-1],
                   url='https://%s:%d/s/%s'%(getip(),myport,imgid),
                   addr=self._address,
                   name=self.name,
                   chatid=self.chatid,)
    def _sendfile(self):
        try:
            if (fp:=askopenfilename())=='':
                return
            open(fp).close()
            fileid=str(time())
            lc.share(fileid,fp)
        except Exception:
            showerror('SWDChat','找不到文件')
            return
        self._send(username=username,
                   type='file',
                   filename=fp.split('/')[-1],
                   url='https://%s:%d/s/%s'%(getip(),myport,fileid),
                   addr=self._address,
                   name=self.name,
                   chatid=self.chatid,)
    def _sendmsg(self):
        s=self.msg.get()
        if not s:
            return
        self.msg.delete(0,'end')
        try:
            s=self.sendcheck(s)
        except StopSending:
            pass
        self._send(username=username,
                   type='msg',
                   msg=s,
                   addr=self._address,
                   name=self.name,
                   chatid=self.chatid,)
    def sendcheck(self,usermsg):
        return usermsg
    def receivecheck(self,received):
        pass
    def mainloop(self):
        def _click(*a):
            try:
                self._sendmsg()
            except Exception as e:
                showerror('ERROR',e)
        def _click_img(*a):
            try:
                self._sendimg()
            except Exception as e:
                showerror('ERROR',e)
        def _click_file(*a):
            try:
                self._sendfile()
            except Exception as e:
                showerror('ERROR',e)
        self.click=_click
        self.fsend=Frame(self.cw)
        self.btns_f=Frame(self.fsend)
        self.msg=Entry(self.fsend)
        self.mtext=ST(self.cw,state='disabled')
        self.mtext.tag_config('orange',foreground='orange')#default_user
        self.mtext.tag_config('red',foreground='red')
        self.b=Button(self.btns_f,text='发送',command=_click)
        self.img_b=Button(self.btns_f,text='发送图片',command=_click_img)
        self.img_f=Button(self.btns_f,text='发送文件',command=_click_file)
        self.cw.bind("<Return>",_click)
        self.msg.pack(side='left',fill=X,expand=True)
        self.b.pack(side='right')
        self.img_b.pack(side='left')
        self.img_f.pack(side='left')
        self.btns_f.pack(side='right')
        self.fsend.pack(fill=X,expand=False)
        self.mtext.pack(fill=BOTH,expand=True)
    def receive(self,s,usern):
        self.receivecheck(s)
        self.mtext.config(state='normal')
        if usern==username:
            try:
                self.mtext.tag_config(self.message_color[0],
                                      foreground=self.message_color[0])
                self.mtext.insert(1.0,s,self.message_color[0])
            except Exception as e:
                print('This exception is from schat window while receiving an message',
                      type(e),e,'\n',sep='\n',file=stderr)
        else:
            try:
                self.mtext.tag_config(self.message_color[1],
                                      foreground=self.message_color[1])
                self.mtext.insert(1.0,s,self.message_color[1])
            except Exception as e:
                print('This exception is from schat window while receiving an message',
                       type(e),e,'\n',sep='\n',file=stderr)
        self.mtext.config(state='disabled')
class SchatWindow(Schat):
    '''\
address:元组，所有人(包括自己)的IP+端口(格式：(IP1,port1),(IP2,port2)...)
可选参数:
size:二元组，(x,y)设定窗口尺寸，默认为(400,650)
message_color:二元组，(color0,color1)，color0指己方消息颜色，color1指对方，
    默认为('black','blue')
title:标题
username:用户名
'''
    size=(400,650)
    title='schat 2024'
    def __init__(self,address:tuple,**options):
        self.cw=Tk()
        super().__init__(address,**options)
    def setwin(self,mode):
        '''设置窗口状态:
    1:显示窗口
    0:隐藏窗口
    -1:销毁窗口
    '''
        if mode==1:
            self.cw.deiconify()
        elif mode==0:
            self.cw.withdraw()
        elif mode==-1:
            self.cw.quit()
            self.cw.destroy()
    def mainloop(self):
        def _click(*a):
            try:
                self._sendmsg()
            except Exception as e:
                showerror('ERROR',e)
        self.cw.title(self.title)
        self.cw.update()
        self.cw.geometry('{}x{}'.format(self.size[0],self.size[1]))
        super().mainloop()
        self.cw.mainloop()
class SchatFrame(Schat):
    def __init__(self,root:Tk,address:tuple,**options):
        self.cw=Frame(root)
        super().__init__(address,**options)
    def mainloop(self):
        def _click(*a):
            try:
                self._sendmsg()
            except Exception as e:
                showerror('ERROR',e)
        super().mainloop()
        #self.cw.pack()
def init(port:int=0):
    global myport
    if lc.init(port):return 1
    myport=lc.httpd.server_port#本机使用的端口(int)
    return 0
#@lc.receive
def receive(obj):
    try:
        chatid=obj[4]
        sobj=win_obj[address]
        s='[%s]%s'%(obj[0],obj[1])
        sobj.receive(s,obj[0])
    except Exception as e:
        print('This exception is from schat server while receiving an object',
              type(e),e,'\n',sep='\n',file=stderr)
if __name__=='__main__':
    init()
    tk=Tk()
    t=SchatFrame(tk,address=((getip(),myport),))
    t.mainloop()
    tk.mainloop()
