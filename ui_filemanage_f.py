# -*- encoding=utf-8 -*-
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


#ui:文件管理
from tkinter import *
from tkinter import messagebox
#from tkinter.tix import ButtonBox
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
import logging
import os

import ui_groupset

def NULL(*args):
    logging.info('An empty function is called with'+str(*args))

fileframestyle=Style()
fileframestyle.configure('filelayout.TFrame',#background='black',
                    foreground='white',relief=SUNKEN)
normalframestyle=Style()
normalframestyle.configure('default.TFrame')
class FileFrame(object):
    def __init__(self,master,filename:str=None,
                 location:str=None,
                 source:str=None,fromuser:str=None,
                 img:PhotoImage=None) -> None:
        self.frame=Frame(master=master,style='filelayout.TFrame')
        self.master=master
        self.bg=''
        self.img=img
        self.location=location
        if self.img:
            self._img_l=Label(master=self.frame,image=img)

        self._text_f=Frame(master=self.frame)
        self._name_l=Label(master=self._text_f,text=filename,font=(15),foreground='blue')
        self._intros=f'''From:{fromuser}  code:{source}'''+ f'''\nloaction:{location}'''
        self._intro_l=Label(master=self._text_f,text=self._intros)

        self._button_f=Frame(master=self.frame,style='default.TFrame')
        self._del_f=NULL
        self._opencata_f=NULL
        self._del_b=Button(master=self._button_f,text='Delete',command=self._del_f)
        self._opencata_b=Button(master=self._button_f,text='打开文件夹',command=self._opencata_f)

    def pack(self):
        if self.img:
            self._img_l.pack(side=LEFT,padx=5,pady=5)
        self._name_l.pack(side=TOP,fill=X,)
        self._intro_l.pack(side=BOTTOM,fill=BOTH,expand=True)
        self._text_f.pack(side=LEFT,padx=5,pady=5)
        self._del_b.pack(side=TOP)
        self._opencata_b.pack(side=TOP)
        self._button_f.pack(side=RIGHT)
        self._text_f.pack(fill=BOTH,expand=True)

    def openfile(self):
        os.system(self.location+''+self.filename)
class FileManageFrame(object):
    ...


#try::
def _demo():
    demotk=Toplevel()
    demotk.geometry('%dx%d'%(700,120))
    a=FileFrame(master=demotk,filename='aaa.data',
                 location="C:/users/gqm/aaa.data",
                 source='wjx',fromuser='baboon',
                 img=PhotoImage(file='.\icons\default.png'))
    a.pack()
    a.frame.pack(expand=True,fill=BOTH)
    a.pack()
    demotk.mainloop()
    
def _demo2():
    demotk=Tk()
    st=Style(master=demotk)
    st.configure('aa.TFrame',background='green')
    a=Frame(master=demotk,style='aa.TFrame')
    l=Label(master=a,text='aaaa',background='')
    l.bind('<ButtonRelease-1>',lambda *args: print('aaa'))
    a.pack(fill=BOTH,expand=True)
    l.pack()
    _name_l=Label(master=demotk,text='aaaaaaa')#,background='ffff00')
    _name_l.pack()
    #_name_l.tag_add('underline','1.0',END)
    #_name_l.tag_configure('underline',underline=True)
    demotk.geometry('%dx%d'%(500,400))
    demotk.mainloop()

def _demo1():
    'demo function'
    demotk=Tk()
    #democf.pack(expand=True,fill=BOTH)
    #b=Button(activebackground='red')
    style1=Style()
    style1.configure('filelayout.TFrame',#background='black',
                    foreground='white',relief=SUNKEN)
    
    #b.pack()
    f=Frame(style='filelayout.TFrame')
    #f.config(style=style1)
    s=Button(master=f)
    a=Entry(master=f)
    b=Entry(master=demotk)
    #c=ButtonBox(master=f)
    #c.pack()
    s.pack()
    a.pack()
    b.pack()
    f.pack(expand=True,fill=BOTH)
    demotk.geometry('%dx%d'%(500,400))
    demotk.update()
    demotk.mainloop()

if __name__=='__main__':
    _demo()
