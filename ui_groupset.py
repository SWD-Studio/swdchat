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

# 241129
# ui:群组设置
from tkinter import *  # @UnusedWildImport
from tkinter import messagebox
from tkinter.ttk import *  # @UnusedWildImport
from tkinter.scrolledtext import ScrolledText
import logging


class UserFrame(object):
    'To creat a user frame show user'

    def __init__(self, master, showname=False) -> None:
        self.showname = showname
        self.frame = Frame(master=master)
        self.master = master
        self._ip_e = Entry(master=self.frame)
        self._port_e = Entry(master=self.frame)
        if self.showname:
            self._name_e = Entry(master=self.frame)
        self.delcallback = lambda: None
        self._delete_b = Button(master=self.frame, text='X', command=self.delcallback)

    def config(self, *args, **kwargs) -> None:
        self._ip_e.config(*args, **kwargs)
        self._port_e.config(*args, **kwargs)
        # self._name_e.config(*args,**kwargs)
        self._delete_b.config(*args, **kwargs)

    def pack(self, locate, location=END) -> None:
        self.locate = locate
        self._ip_e.pack(side='left')
        self._port_e.pack(side='left', after=self._ip_e)
        self._delete_b.pack(side='right')
        if self.showname:
            self._name_e.pack(side='right', after=self._delete_b)
            self._name_e.config(state='disabled')
        locate.window_create(location, window=self.frame)
    
    def insert(self, ip:str=None, port:str=None, username=None) -> None:
        'Setting texts of Entrys'
        if ip:
            self._ip_e.insert(1, ip)
        if port:
            self._port_e.insert(1, port)
        if self.showname and username:
            self._name_e.insert(1, username)
    
    def set_name(self, username) -> None:
        if not self.showname: return None
        self._name_e.config(state='normal')
        if username:
            self._name_e.insert('0', username)
        self._name_e.config(state='disabled')
    
    def get_name(self) -> str:
        if self.showname:
            return self._name_e.get()
        return ''
    
    def fetch(self) -> tuple:
        'fetch all users'
        return (self._ip_e.get(), self._port_e.get())

    def delete(self, func):  # @
        '装饰器函数，用于绑定用户删除按钮对应'
        def delcb(self=self):
            return func(self)
        self.delcallback = delcb
        print(self.frame.winfo_geometry())
        self._delete_b.config(command=self.delcallback)
        return func


NEW = False
CONFIG = True


class GroupSetFrame(object):
    'To create a "create frame"'

    def __init__(self, master=None, method=NEW) -> None:
        if master:
            self.frame = Frame(master=master)
        else:
            logging.debug('ignore master')
            self.frame = Frame()
        self.method = method
        self._initsets = None
        self._cancelf = self.reset
        # top lable
        self._top_l = Label(text='在此创建新会话'
                          if self.method == NEW else 
                          '在此修改群组'
                         , master=self.frame)
        # name config area
        self._name_f = Frame(master=self.frame)
        self._name_l = Label(master=self._name_f, text='名称')
        self._name_e = Entry(master=self._name_f, text='Name')
        # main scrolledtext
        self._main_s = ScrolledText(master=self.frame)
        # buttons
        self._button_f = Frame(master=self.frame)
        self._cancel_b = Button(master=self._button_f, text='取消' if self.method == NEW else '删除', command=self._cancelf)
        self._add_b = Button(master=self._button_f, text='添加用户', command=self.add_blank)
        self._confirm_b = Button(master=self._button_f, text='确定', command=self.getall)
        self._reset_b = Button(master=self._button_f, text='重置', command=self.reset)
        # Window arrange
        self._top_l.pack(side='top', fill='x')
        self._name_l.pack(side='left')
        self._name_e.pack(side='right', fill='x', expand=True)
        self._name_f.pack(after=self._top_l, side='top', fill='x')
        self._main_s.pack(side='top', fill='both', expand=True)
        self._button_f.pack(side='bottom', fill='x')
        self._cancel_b.pack(side='left')
        self._confirm_b.pack(side='right')
        self._reset_b.pack(side='left')
        self._add_b.pack(side='right')
        # self.frame.pack(fill='both',expand=True)
        # Window arrange ends
        self._count_user=0
        self.respons = self.egg
        self.reset()

    def __del__(self) -> None:
        'Warn not to delete the frame'
        if self.method == NEW:
            logging.warning('An GroupSetFrame is deleted!')
    
    def initsets(self, name:str, users:list, showuser:bool=True):
        '''
name:群组名称
users:[{'ip':str,'port':str,'username':str},...]
        '''
        self._initsets = [name, users]

    def egg(self) -> None:
        'Easter Egg'
        messagebox.showinfo('Egg',
                           'Tell me what to do next:-)')
    
    def cancel(self, func) -> None:  # @
        '''
设置cancel按钮绑定'''
        self._cancelf = func
        self._cancel_b.config(command=self._cancelf)
        return func

    def add_blank(self):
        'add an new blank user area'
        user = UserFrame(master=self.frame, showname=self.method)

        def dele(self,tag:str=str(self._count_user), master=self._main_s, uslist:list=self.userlist):
            master.config(state='normal')
            master.delete(master.tag_ranges(tag)[0], master.tag_ranges(tag)[1])
            master.update()
            uslist.remove(self)
            master.config(state='disabled')
        
        user.delete(dele)
        self.userlist.append(user)
        self._main_s.config(state='normal')
        user.pack(locate=self._main_s)
        self._main_s.insert(index=END, chars='\n')
        
        self._main_s.tag_add(str(self._count_user),float(len(self.userlist) + 1), float(len(self.userlist) + 2))
        self._count_user+=1
        self._main_s.config(state='disabled')

    def add_user(self, user=None, port=None, username=None, state='normal'):
        'add an new user'
        self.add_blank()
        self.userlist[-1].insert(ip=user, port=port)
        self.userlist[-1].set_name(username=username)
        self.userlist[-1].config(state=state)

    def set_name(self, name:str=None, state='normal') -> None:
        if name:
            self._name_e.insert('0', name)
        self._name_e.config(state=state)

    def getall(self) -> list:
        'get all user information'
        newn = self._name_e.get()
        if not newn:  # 空白
            messagebox.showerror('SWDChat', '名称中不能留空')
            self._name_e.focus_set()
            return
        if ' ' in newn:  # 有空格
            # print(self.frame.winfo_geometry(),self.frame.winfo_height(),self.frame.winfo_width())
            messagebox.showerror('SWDChat', '名称中不能有空格')
            return
        userset = set()
        for i in self.userlist:
            k = i.fetch()
            try:
                uport = int(k[1])
            except Exception:  # 若端口留空则用本机端口
                uport = int(MYPORT)
            try:  # 数IP的后缀数
                l = k[0].count('.')
            except IndexError:
                continue
            temp = MYIP.split('.')[:3 - l]  # 加上各段IP
            temp.append(k[0])
            ip = '.'.join(temp)
            if k[0].strip() == '':
                ip = MYIP
            if self.method == NEW:  # 加入用户信息
                userset.add((ip, uport,))
            else:
                userset.add((ip, uport, i.get_name()))
        userlist = []
        for i in userset:userlist.append(list(i[0:2]))
        if self.method == CONFIG:
            userdics = []
            for i in userset: userdics.append({'ip':i[0], 'port':i[1], 'username':i[2]})
            self._initsets = [self._name_e.get(), userdics]
        self.respons(self._name_e.get(), userlist)
        self.reset()
        
    def fetch(self, func):  # @
        'configure what to do when user click button'
        self.respons = func
        return func

    def reset(self, clear=False):
        'reset the frame'
        self._main_s.config(state='normal')
        self._main_s.delete('1.0', END)
        self._name_e.delete(0, END)
        # it is pazzling why we cannot just do this once
        # what a fucking interpreter
        self._name_e.delete(0, END)
        self.userlist = []
        if self.method:
            self._main_s.insert(1.0, 'IP                   端口号                 用户名\n')
        else:
            self._main_s.insert(1.0, 'IP                   端口号\n')
        self.add_user(user=MYIP, port=MYPORT, username='本机', state='disabled')
        if not clear and self._initsets and self.method:
            # print(users,len(users))
            name = self._initsets[0]
            users = self._initsets[1]
            self._name_e.insert(0, name)
            for i in users:
                print(i)
                if i['ip'] == MYIP and str(i['port']) == str(MYPORT):continue
                self.add_user(i['ip'], str(i['port']), i['username'])
            # self.initsets(self._initsets[0],self._initsets[1])
        self._main_s.config(state='disabled')


MYIP = '172.168.50.144'
MYPORT = '19198'


def ipconfig(ip:str, port:str) -> None:
    '设置我的IP和端口'
    global MYIP, MYPORT
    MYIP = ip
    MYPORT = str(port)


def _demo():
    'demo function'
    demotk = Tk()
    democf = GroupSetFrame(master=demotk, method=NEW)  # 实例化一个GroupSetFrame对象
    democf.frame.pack()
    democf.fetch(func=lambda *args:print(*args))  # 将这个无名函数绑定到Confirm的响应事件上（第一个位置参数为名字，第二个是你要的set）
    demotk.geometry('%dx%d' % (1000, 700))
    democf.add_user('test1', '')
    demotk.update()
    demotk.mainloop()


if __name__ == '__main__':
    _demo()
