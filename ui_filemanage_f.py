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
        self.filename=filename
        if self.img:
            self._img_l=Label(master=self.frame,image=img)

        self._text_f=Frame(master=self.frame)
        self._name_l=Label(master=self._text_f,text=self.filename,font=(15),foreground='blue')
        self._name_l.bind('<ButtonRelease-1>',self.openfile)
        self._intros=f'''From:{fromuser}  code:{source}'''+ f'''\nloaction:{location}'''
        self._intro_l=Label(master=self._text_f,text=self._intros)

        self._button_f=Frame(master=self.frame,style='default.TFrame')
        self._del_f=NULL
        self._opencata_f=self.openfiledir
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

    def openfile(self,*args):
        if args:
            logging.info('file open is called'+str(args))
        print(self.location+'''\\'''+self.filename)
        os.startfile(self.location+'''\\'''+self.filename)

    def openfiledir(self)->None:
        os.system("explorer.exe "+self.location)

    def delete(self,func):#@
        self._del_f=func
        self._del_b.config(command=self._del_f)
        return func

class FileManageFrame(object):
    ...


#try::
def _demo():
    demotk=Toplevel()
    demotk.geometry('%dx%d'%(700,120))
    a=FileFrame(master=demotk,filename='license.txt',
                 location=".",
                 source='wjx',fromuser='baboon',
                 img=PhotoImage(file='.\icons\default.png'))
    a.pack()
    a.frame.pack(expand=True,fill=BOTH)
    a.delete(lambda :print('aaa'))
    a.pack()
    demotk.mainloop()
    
    
if __name__=='__main__':
    _demo()
