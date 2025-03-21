#    Copyright (C) 2020-2024  SWD Studio

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

# 20250305
# ui:用户设置

from tkinter import *  # @UnusedWildImport
from tkinter import filedialog
from tkinter.ttk import *  # @UnusedWildImport
from threading import Thread
import logging

from scicons import iconmap


def nullfunc(*args):
    pass


MYIP = '172.168.50.144'
MYPORT = '19198'

# ihtrupyehj = Style()
# ihtrupyehj.configure('rl.TEntry', state='readonly')

setmsg = '''\

This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome redistribute it under certain conditions.
See the GNU General Public License for more details.

You can contact us on <swdstudio.github.io>.
SWDChat {v} Copyright (C) 2020-2025 SWD Studio
'''


class MainSetFrame(object):
    'To create a "main setting frame"'

    def __init__(self, username:str, master=None) -> None:
        if master:
            self.frame = Frame(master=master)
        else:
            logging.debug('ignore master')
            self.frame = Frame()

        self.setpathfunc = nullfunc
        self.setconfirmfunc = nullfunc
        self._username = username
        self._default_path = ''

        self._myip_l = Label(self.frame, text='本机IP:%s\n本机端口:%s' % (MYIP, MYPORT))  # IP及端口信息

        self._name_f = Frame(self.frame)  # 用户名设定
        self._name_l = Label(self._name_f, text='用户名:')
        self._name_e = Entry(self._name_f, text=username)

        self._path_f = Frame(self.frame)  # 下载路径设定
        self._path_l = Label(self._path_f, text='默认下载路径:')
        self._path_e = Label(self._path_f, background='white',)  # text='%USERPROFILE%/Download/SC')
        
        self._path_b = Button(self._path_f, image=iconmap['FOLDER'], command=self._sdf)
        self._set_b = Button(self.frame, text='保存设置', command=self._setting)
        self.del_b = Button(self.frame, text='退出', command=nullfunc)
        
        # 许可证，免责声明，退出
        self._notice_l = Label(master=self.frame, text=setmsg.format(v=version))
        
        self._close_f = Frame(self.frame)
        
        # Label控件
        self._close_l = Label(self._close_f, text="选择您希望点击右上角关闭按钮的操作:", justify=LEFT)

        # Radiobutton 控件（单选按钮）
        self._del_option_v = IntVar()
        self.del_option_v = 0
        # 使用Radiobutton类的实例对象向root窗口添加单选按钮控件
        self._del_option_1 = Radiobutton(self._close_f, text="最小化到托盘区", variable=self._del_option_v, value=1)
        self._del_option_2 = Radiobutton(self._close_f, text="关闭程序(无法接收此后信息)", variable=self._del_option_v, value=0)

    def pack(self):
        self._myip_l.pack(side='top', fill='x')

        self._name_l.pack(side='left')
        self._name_e.pack(side='right', fill='x', expand=True)  # ,ipadx=85)
        self._name_f.pack(side='top', fill='x')

        self._path_l.pack(side='left')
        self._path_b.pack(side='right')
        self._path_e.pack(side='right', after=self._path_b, fill='x', expand=True)
        self._path_f.pack(side='top', fill='x')
        
        self._close_l.pack(side=LEFT)
        self._del_option_1.pack(side=LEFT)
        self._del_option_2.pack(side=LEFT)
        self._close_f.pack(fill=X)

        self.del_b.pack(side=BOTTOM, fill=X)
        self._set_b.pack(side=BOTTOM, fill=X)
        self._notice_l.pack(fill=X, side=BOTTOM)

        self.frame.pack(fill='both', expand=True)

    def _setpath(self):  # 设定下载路径
        self._path_e['text'] = filedialog.askdirectory()

    def pathset(self, func):  # @
        self.setpathfunc = func
        return func

    def _sdf(self):  # 设定下载路径
        self.sdfth = Thread(daemon=True, target=self._setpath)
        self.sdfth.start()

    def _setting(self):
        self._default_path = self._path_e['text']
        self._username = self._name_e.get()
        self.del_option_v = self._del_option_v.get()
        self.setconfirmfunc()
        self.setpathfunc(self._default_path)

    def setting(self, func):  # 保存设置 
        self.setconfirmfunc = func
        return func

    def reset(self):
        self._name_e.delete(0, 'end')
        self._name_e.insert(0, self.username)
        self._path_e['text'] = self.default_path
        self._del_option_v.set(self.del_option_v)

    def setup(self, username, path, del_option):
        
        self._default_path , self._path_e['text'] = path , path
        self._username = username 
        self._name_e.insert(0, username)
        self._del_option_v.set(del_option)
        self.del_option_v = del_option

    @property
    def default_path(self):
        return self._default_path

    @property
    def username(self):
        return self._username


def ipconfig(ip:str, port:str) -> None:
    '设置我的IP和端口'
    global MYIP, MYPORT
    MYIP = ip
    MYPORT = str(port)


def config(vers:str) -> None:
    '''设置版本'''
    global version
    version = vers


def _demo():
    'demo function'
    global version

    def test(inp):
        print (inp)

    version = 'test'
    demotk = Tk()
    demomsf = MainSetFrame(master=demotk, username='GQM')  # 实例化一个MainSetFrame对象
    demomsf.setting(test)
    demomsf.pathset(lambda a:print(demomsf.username, demomsf.default_path))
    demomsf.pack()
    demomsf.setup('aa', 'bb', True)
    demotk.geometry('%dx%d' % (1000, 700))
    demotk.update()
    demotk.mainloop()


if __name__ == '__main__':
    _demo()
