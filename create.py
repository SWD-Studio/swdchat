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
#    You can contact us on swd-go.ys168.com.

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from tkinter.scrolledtext import ScrolledText
import logging
class UserFrame(object):
    'To creat a user frame show user'
    def __init__(self,user=None,port=None) -> None:
        pass

class CreateFrame(object):
    'To create a "create frame"'
    def __init__(self,master=None):
        if master:
            self.frame=Frame(master=master)
        else:
            logging.debug('ignore master')
            self.frame=Frame()
        #top lable
        self._top_l=Label(text='You can create a new conversation here.',master=self.frame)
        #name config area
        self._name_f=Frame()
        self._name_l=Label(master=self._name_f,text='Name')
        self._name_e=Entry(master=self._name_f,text='Name')
        #main scrolledtext
        self._main_s=ScrolledText(master=self.frame)#,height=50,width=140)
        #buttons
        self._button_f=Frame(master=self.frame)
        self._cancel_b=Button(master=self._button_f,text='Cancel',command=self.reset)
        self._add_b=Button(master=self._button_f,text='Add',command=self.add_blank)#Unfinished
        self._confirm_b=Button(master=self._button_f,text='Confirm',command=self.getall)
        # Window arrange
        self._top_l.pack(side='top',fill='x')
        self._name_f.pack(after=self._top_l,side='top',fill='x')
        self._name_l.pack(side='left')
        self._name_e.pack(side='right',fill='x',expand=True)
        self._main_s.pack(side='top',fill='both',expand=True)
        self._button_f.pack(side='bottom',fill='x')
        self._cancel_b.pack(side='left')
        self._confirm_b.pack(side='right')
        self._add_b.pack(side='right')
        self.frame.pack(fill='both',expand=True)
        # Window arrange ends
        self.respons=self.egg
    def __del__(self)->None:
        'Warn not to delete the frame'
        logging.warning('You can not delete the create frame!')
    
    def egg(self):
        'Easter Egg'
        messagebox.showinfo('Egg','GQM loves WJX,but he forgot to config what to do next.')
    def add_blank():
        'add an new blank user area'
        ...
    def add_user(user=None,port=None):
        'add an new user'
        ...
        '''
        a=Button()
        main_s.window_create('End',window=a)
        '''

    def getall(self):
        'get all user imformation'
        self.respons(...)
        ...
    def fetch(self,func): #@
        'config what to do when user click button'
        self.respons=func
        return func

    def reset(self):
        'reset the frame'
        ...

def _demo():
    'demo function'
    demotk=Tk()
    democf=CreateFrame(master=demotk)
    democf.fetch(func=lambda a:print(a))
    demotk.geometry('%dx%d'%(1000,700))
    demotk.update()
    demotk.mainloop()
if __name__=='__main__':
    _demo()