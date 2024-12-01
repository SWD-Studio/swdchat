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
#    You can contact us on swd-go.ysepan.com.

# 20241201
# SWDChat专用版
# 按钮被禁用时忽略回车键
# _send方法可以设定为不发送
import swdlc as lc
from swdlc import getip
from threading import Thread
from tkinter import *  # @UnusedWildImport
from tkinter.filedialog  import *  # @UnusedWildImport
from tkinter.scrolledtext import ScrolledText as ST
from tkinter.ttk import *  # @UnusedWildImport
from tkinter.messagebox import showerror
from time import localtime, strftime, time

# 消息传递格式(不同类型的消息可能略有不同)
# {'username':用户名,'type':内容类型,'msg':内容,
# 'addr':地址,'name':群组名,'chatid':群组id,
# 'from':(IP,port),'addrver':用户列表版本，即更新时间}

username = getip()  # 默认用户名
myport = 0


class StopSending(Exception):pass


def gettime():  # 获取系统时间
    t = strftime("%X", localtime())
    return t[:t.rfind(':')]


class SchatFrame(object):
    buttons = {}
    enable_TLS = True
    message_color = ('black', 'blue')
    enable_tips = True
    name = ''  # name of this Schat
    disabled = False

    def __init__(self, root:Tk, address:list, **options):
        self.cw = Frame(root)
        self.address = address
        self.addrver = str(time())
        for i in options:
            exec('self.%s=%s' % (i, repr(options[i])))
        self.chatid = str(time())  # 缺省chatid

    def _send(self, send=True, **kwargs):

        def sending(kwargs, ip, port):
            try:
                lc.send(kwargs, ip, port)
            except Exception as e:
                self.mtext.config(state='normal')
                self.mtext.insert('1.0', f'消息在发送到{ip}:{port}时发生错误。\n', 'red')
                self.mtext.config(state='normal')

        kwargs['username'] = username
        kwargs['addr'] = self.address
        kwargs['name'] = self.name
        kwargs['chatid'] = self.chatid
        kwargs['from'] = '{}:{}'.format(getip(), myport)
        kwargs['addrver'] = self.addrver
        if send:
            for ip, port in self.address:
                Thread(target=sending,
                       args=((kwargs, ip, str(port)))).start()
        else:
            return kwargs

    def sendnew(self, send=True, addr=None):
        if addr:
            self.addr = addr
        return self._send(send,
                          type='new',
                          )

    def _sendimg(self, send=True):
        try:
            if (fp := askopenfilename()) == '':
                return
            open(fp).close()
            imgid = str(time())
            lc.share(imgid, fp, len(self.address))
        except Exception as e:
            showerror('SWDChat', '找不到文件' + str(e))
            return
        return self._send(send,
                          type='img',
                          imgname=fp.split('/')[-1],
                          url='https://%s:%d/s/%s' % (getip(), myport, imgid),
                          )

    def _sendfile(self, send=True):
        try:
            if (fp := askopenfilename()) == '':
                return
            open(fp).close()
            fileid = str(time())
            lc.share(fileid, fp)
        except Exception:
            showerror('SWDChat', '找不到文件')
            return
        return self._send(send,
                          type='file',
                          filename=fp.split('/')[-1],
                          url='https://%s:%d/s/%s' % (getip(), myport, fileid),
                          )

    def _sendmsg(self, send=True):
        s = self.msg.get()
        if not s:
            return
        try:
            s = self.sendcheck(s)
        except StopSending:
            pass
        self.msg.delete(0, 'end')
        return self._send(send,
                          type='msg',
                          msg=s,
                          )

    def sendcheck(self, s):
        return s

    def modify(self):
        pass

    def click(self, *a):  # @UnusedVariable
        if self.disabled:
            return
        self._click()

    def mainloop(self):

        def _click(*a):  # @UnusedVariable
            try:
                self._sendmsg()
            except Exception as e:
                showerror('ERROR', e)

        def _click_img(*a):  # @UnusedVariable
            try:
                self._sendimg()
            except Exception as e:
                showerror('ERROR', e)

        def _click_file(*a):  # @UnusedVariable
            try:
                self._sendfile()
            except Exception as e:
                showerror('ERROR', e)

        def _click_modify(*a):  # @UnusedVariable
            try:
                self.modify(self)
            except Exception as e:
                showerror('ERROR', e)

        self._click = _click
        self.fsend = Frame(self.cw)
        self.btns_f = Frame(self.fsend)
        self.msg = Entry(self.fsend)
        self.mtext = ST(self.cw, state='disabled')
        self.mtext.tag_config('orange', foreground='orange')
        self.mtext.tag_config('red', foreground='red')
        self.mtext.tag_config('blue', foreground='blue')
        self.buttons['msg'] = Button(self.btns_f, text='发送', command=_click)
        self.buttons['img'] = Button(self.btns_f, text='发送图片', command=_click_img)
        self.buttons['file'] = Button(self.btns_f, text='发送文件', command=_click_file)
        self.buttons['modify'] = Button(self.btns_f, text='修改群组', command=_click_modify)
        self.cw.bind("<Return>", _click)
        self.msg.pack(side='left', fill=X, expand=True)
        self.buttons['msg'].pack(side='right')
        self.buttons['img'].pack(side='left')
        self.buttons['file'].pack(side='left')
        self.buttons['modify'].pack(side='left')
        self.btns_f.pack(side='right')
        self.fsend.pack(fill=X, expand=False)
        self.mtext.pack(fill=BOTH, expand=True)


def init(port:int=0):
    global myport
    if lc.init(port):return 1
    myport = lc.httpd.server_port  # 本机使用的端口(int) @UndefinedVariable
    return 0
