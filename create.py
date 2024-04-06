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

class CreateFrame(object):
    'To create a "create frame"'
    def __init__(self,master=None):
        if master:
            self.frame=Frame(master=master)
        else:
            logging.debug('ignore master')
            self.frame=Frame()
        self._top_l=Label(text='You can create a new conversation here.',master=self.frame)
        self._main_s=ScrolledText(master=self.frame)#,height=50,width=140)
        self._button_f=Frame(master=self.frame)
        self._cancel_b=Button(master=self._button_f,text='Cancel',command=self.reset)
        self._add_b=Button(master=self._button_f,text='Add',command=self.add_user)#Unfinished
        self._confirm_b=Button(master=self._button_f,text='Confirm',command=self.getall)
        # Window arrange
        self._top_l.pack(side='top')
        self._main_s.pack(side='top',fill='both',expand=True)
        self._button_f.pack(side='bottom',fill='x')
        self._cancel_b.pack(side='left')
        self._confirm_b.pack(side='right')
        self.frame.pack(fill='both',expand=True)
        # Window arrange ends
        self.respons=self.egg
    def __del__(self)->None:
        logging.warn('You can not delete the create frame!')
    
    def egg(self):
        messagebox.showinfo('Egg','GQM loves WJX,but he forgot to config what to do next.')

    def add_user(user=None,port=None):
        ...
        '''
        a=Button()
        main_s.window_create('End',window=a)
        '''

    def getall(self):
        self.respons(...)
        ...
    def fetch(self,func): #@
        'config what to do when user click button'
        self.respons=func
        return func

    def reset(self):
        ...

def _demo():
    demotk=Tk()
    democf=CreateFrame(master=demotk)
    democf.fetch(func=lambda a:print(a))
    demotk.geometry('%dx%d'%(1000,700))
    demotk.update()
    demotk.mainloop()
if __name__=='__main__':
    _demo()