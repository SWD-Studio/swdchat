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
#    You can contact us on <http://swd-go.ysepan.com>.

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
import logging

class UserFrame(object):
    'To creat a user frame show user'
    def __init__(self,master,user=None,port=None) -> None:
        self.frame=Frame(master=master)
        self.master=master
        self._ip_e=Entry(master=self.frame)
        self._port_e=Entry(master=self.frame)
        self.delcallback=lambda : None
        self._delete_b=Button(master=self.frame,text='X',command=self.delcallback)

    def config(self,*args,**kwargs) -> None:
        self._ip_e.config(*args,**kwargs)
        self._port_e.config(*args,**kwargs)
        self._delete_b.config(*args,**kwargs)

    def pack(self,locate,location=END) -> None:
        self.locate=locate
        self._ip_e.pack(side='left')
        self._port_e.pack(side='left',after=self._ip_e)
        self._delete_b.pack(side='right')
        locate.window_create(location,window=self.frame)
    
    def insert(self,ip:str=None,port:str=None) -> None:
        'Setting texts of Entrys'
        if ip:
            self._ip_e.insert(1,ip)
        if port:
            self._port_e.insert(1,port)
    
    def fetch(self) -> tuple:
        'fetch all users'
        return (self._ip_e.get(),self._port_e.get())

    def delete(self,func):#@
        '装饰器函数，用于绑定用户删除按钮对应'
        self.delcallback=func
        self._delete_b.config(command=self.delcallback)
        return func

class CreateFrame(object):
    'To create a "create frame"'
    def __init__(self,master=None) -> None:
        if master:
            self.frame=Frame(master=master)
        else:
            logging.debug('ignore master')
            self.frame=Frame()
        #top lable
        self._top_l=Label(text='You can create a new conversation here.'
                         ,master=self.frame)
        #name config area
        self._name_f=Frame()
        self._name_l=Label(master=self._name_f,text='Name')
        self._name_e=Entry(master=self._name_f,text='Name')
        #main scrolledtext
        self._main_s=ScrolledText(master=self.frame)#,height=50,width=140)
        #buttons
        self._button_f=Frame(master=self.frame)
        self._cancel_b=Button(master=self._button_f,text='Cancel',command=self.reset)
        self._add_b=Button(master=self._button_f,text='Add',command=self.add_blank)
        self._confirm_b=Button(master=self._button_f,text='Confirm',command=self.getall)
        self._reset_b=Button(master=self._button_f,text='Reset',command=self.reset)
        # Window arrange
        self._top_l.pack(side='top',fill='x')
        self._name_f.pack(after=self._top_l,side='top',fill='x')
        self._name_l.pack(side='left')
        self._name_e.pack(side='right',fill='x',expand=True)
        self._main_s.pack(side='top',fill='both',expand=True)
        self._button_f.pack(side='bottom',fill='x')
        self._cancel_b.pack(side='left')
        self._confirm_b.pack(side='right')
        self._reset_b.pack(side='left')
        self._add_b.pack(side='right')
        self.frame.pack(fill='both',expand=True)
        # Window arrange ends
        self.respons=self.egg
        self.reset()

    def __del__(self) -> None:
        'Warn not to delete the frame'
        logging.warning('You can not delete the create frame!')
    
    def egg(self) -> None:
        'Easter Egg'
        messagebox.showinfo('Egg',
                           'GQM loves WJX,but he forgot to config what to do next:-)')
    def add_blank(self):
        'add an new blank user area'
        user=UserFrame(master=self.frame)
        def dele(position:int=len(self.userlist),master=self._main_s,uslist:list=self.userlist):
            master.config(state='normal')
            master.delete(float(position+2),float(position+3))
            uslist.pop(position)
            master.config(state='disabled')
            
        user.delete(dele)
        self.userlist.append(user)
        self._main_s.config(state='normal')
        user.pack(locate=self._main_s)
        self._main_s.insert(index=END,chars='\n')
        self._main_s.config(state='disabled')

    def add_user(self,user=None,port=None,state='normal'):
        'add an new user'
        self.add_blank()
        self.userlist[-1].insert(ip=user,port=port)
        self.userlist[-1].config(state=state)

    def getall(self):
        'get all user imformation'
        newn=self._name_e.get()
        if not newn:#空白
            messagebox.showerror('SWDChat','名称中不能留空')
            self._name_e.focus_set()
            return
        if ' ' in newn:#有空格
            messagebox.showerror('SWDChat','名称中不能有空格')
            return
        userset=set()
        for i in self.userlist:
            userset.add(i.fetch())
        self.respons(self._name_e.get(),userset)
        self.reset()
        
    def fetch(self,func): #@
        'config what to do when user click button'
        self.respons=func
        return func

    def reset(self):
        'reset the frame'
        self._main_s.config(state='normal')
        self._main_s.delete('1.0',END)
        self._name_e.delete('1',END)
        self.userlist=[]
        self._main_s.insert(1.0,'IP                   PORT\n')
        self.add_user(user=MYIP,port=MYPORT,state='disabled')
        self._main_s.config(state='disabled')


MYIP='172.168.50.144'
MYPORT='19198'

def ipconfig(ip:str,port:str)->None:
    '设置我的IP和端口'
    global MYIP,MYPORT
    MYIP=ip
    MYPORT=port

def _demo():
    'demo function'
    demotk=Tk()
    democf=CreateFrame(master=demotk)#实例化一个CreateFrame对象
    democf.fetch(func=lambda *args:print(*args))#将这个无名函数绑定到Confirm的响应事件上（第一个位置参数为名字，第二个是你要的set）
    demotk.geometry('%dx%d'%(1000,700))
    demotk.update()
    demotk.mainloop()

if __name__=='__main__':
    _demo()

'''
写在最后的话:
键盘控制的部分来不及写了，要不你写或者等我回来写吧
'''