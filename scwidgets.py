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

#version 241218 


from tkinter import *  # @UnusedWildImport
from tkinter.ttk import *

from PIL import Image, ImageTk

from multiplatform import open_file
class ProcessBar(object):
    '''an processbar wegid'''
    def __init__(self, master, height:int) -> None:
        self.frame = Frame(master=master, height=height)
        self._bar = Frame(master=self.frame, height=height, style='bluef.TFrame')
        self._bar.configure(width=0)

    def setpro(self, proce:float):
        '''proce:float type,between 0.0-1.0'''
        width = self.frame.winfo_width()
        bar_width = width * proce
        self._bar.configure(width=bar_width)

    def pack(self, *args, **kwargs) -> None:
        '''Pack a widget in the parent widget. Use as options: 
after=widget - pack it after you have packed widget 
anchor=NSEW (or subset) - position widget according togiven direction
before=widget - pack it before you will pack widget 
expand=bool - expand widget if parent size grows 
fill=NONE or X or Y or BOTH - fill widget if widget grows in=
master - use master to contain this widget in_=master - see 'in' option description 
ipadx=amount - add internal padding in x direction 
ipady=amount - add internal padding in y direction 
padx=amount - add padding in x direction 
pady=amount - add padding in y direction 
side=TOP or BOTTOM or LEFT or RIGHT - where to add this widget.'''
        self._bar.pack(side=LEFT,)
        self.frame.pack(*args, **kwargs)

    def setstyle(self, style:str):
        '''set the bar's style,Using TFrame'''
        self._bar.config(style=style)


class ImageDisplayLabel(Label):
    '''To display a Image'''
    def __init__(self,img_path:str,width:int=None,height:int=None,*args,**kwargs) -> None:
        '''initial set up'''
        self.img_path=img_path
        self.img_open= Image.open(img_path)
        max_size=(width,height)
        self.img_open.thumbnail(max_size)  # 使用 thumbnail() 方法创建缩略图
        self.img_tk=ImageTk.PhotoImage(self.img_open)
        Label.__init__(self,width=width,image=self.img_tk,*args,**kwargs)
        self.bind('<ButtonRelease-1>', self.openfile)

    def openfile(self,*args):
        open_file(self.img_path)


def pt16(img_path:str)->PhotoImage:
    img_open= Image.open(img_path)
    max_size=(24,24)
    img_open.thumbnail(max_size)
    return ImageTk.PhotoImage(img_open)

if __name__ == '__main__':
    demotk = Tk()
    demotk.geometry('%dx%d' % (509*2, 652))
    aaa=ImageDisplayLabel(img_path='./icons/default.png',width=50,height=50,master=demotk)
    aaa.pack()
    demotk.mainloop()
