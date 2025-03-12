#    Copyright (C) 2020-2025  SWD Studio

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

# ui:关于（首页）
#250109
from tkinter import *  # @UnusedWildImport
from tkinter.ttk import *  # @UnusedWildImport
import logging


from PIL import Image, ImageTk


class AboutFrame(object):
    '''To creat a frame to show "about"'''

    def __init__(self, master=None) -> None:
        if master:
            self.frame = Frame(master=master)
        else:
            logging.debug('ignore master')
            self.frame = Frame()
        self.frame = Frame(master)
        # main scrolledtext
        self._main_st = Text(self.frame)
        # self._main_st.pack(fill=BOTH,expand=True)

        
        img_dir = './icons/welcome.jpg'
        img_open = Image.open(img_dir)
        self._img_tk = ImageTk.PhotoImage(img_open)
        self._img_l = Label(image=self._img_tk)

        self._main_st.config(font=('Consolas', 20))  # 设置字体
        self._main_st.insert(1.0,f'''\
        精简，但更精妙
        SWDChat Version {version}''')
        self.btns={}
        
    
    def pack(self) -> None:
        self._main_st.pack(side='top', fill='both', expand=True)
        
        self._main_st.window_create(1.0,window=self._img_l)
        for i in self.btns:
            self._main_st.insert(END,'\n\t')
            self._main_st.window_create(END,window=self.btns[i])
        self.frame.pack(fill='both', expand=True)
        self._main_st.config(state='disabled')


version = 'TESTVERSION'


def config(vers:str) -> None:
    '''设置版本'''
    global version
    version = vers


def _demo():
    '''demo function'''
    demotk = Tk()
    demotk.geometry('%dx%d' % (1000, 700))
    demoaf = AboutFrame(master=demotk)  # 实例化一个CreateFrame对象
    demoaf.pack()
    demotk.update()
    demotk.mainloop()


if __name__ == '__main__':
    _demo()
