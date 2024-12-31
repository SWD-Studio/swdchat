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

_updated_='20241230'
#slight change
import logging
import threading
import json

# ui:文件管理
from tkinter import *  # @UnusedWildImport
from tkinter import messagebox
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *
from typing import Any
from urllib.error import HTTPError, URLError

import swdlc
from multiplatform import *
from scwidgets import ProcessBar
from scicons import iconmap

def NULL(*args):
    '''empty function'''
    logging.info('An empty function is called with %s'%str(*args))


def getimg(filename:str) -> PhotoImage:
    '''get a PhotoImage (Tk) by filetype'''
    formation=os.path.splitext(filename)[-1]
    if formation[0] == '.':
        formation=formation[1:]
    with open('./icons/files/catalog.json', encoding='utf-8') as file:
        imglist=file.read()
    filelist=json.loads(imglist)
    if formation in filelist:
        return PhotoImage(file='./icons/files/'+formation+'.png')
    return PhotoImage(file='./icons/files/nofile.png')


def sizetransform(size:str) -> str:
    '''transform file size into proper unit'''
    size = int(size)
    units = ['B','kB','MB','GB']
    for i in units:
        if size <= 1024:
            return '%.2f'%size + i
        size /= 1024
    return '%.2f'%size + 'TB'


def ipfill(ip:str, port:str):
    '''fill IP and port automatically'''

    try:  # 数IP的后缀数
        l = ip.count('.')
    except IndexError:
        logging.info('Bad user input')
    uip = '.'.join(MYIP.split('.')[:3 - l] + [ip])
    port = str(port) if port else str(MYPORT)  # 若端口留空则用本机端口
    if ip.strip() == '':
        uip = MYIP
    return uip, port


fileframestyle = Style()
fileframestyle.configure('filelayout.TFrame',  # background='black',
                    foreground='white', relief=SUNKEN)
normalframestyle = Style()
normalframestyle.configure('default.TFrame')
bluesty = Style()
bluesty.configure('bluef.TFrame', background='#46ade0')
redsty = Style()
redsty.configure('redf.TFrame', background='red')
graysty = Style()
graysty.configure('grayf.TFrame', background='gray')


class FileFrame(object):
    '''the frame object to showcase a file'''
    def __init__(self, master, width:int=None,
                 filename:str=None,
                 location:str=None, size:int=0,
                 code:str=None, fromuser:str=None,
                 fromport:int=None,
                 img:PhotoImage=None) -> None:
        self.frame = Frame(master=master, style='filelayout.TFrame', 
                           width=width, height=190)
        self.frame.pack_propagate(False)
        self.master = master
        self.bg = ''
        self.img = img
        self.location = location
        self.filename = filename
        self.size = size
        self.fromip = fromuser
        self.fromport = fromport
        self.code = code

        self._main_f = Frame(master=self.frame)
        if self.img:
            self._img_l = Label(master=self._main_f, image=img)

        self._text_f = Frame(master=self._main_f,width=width-400 if width>400 else 200)
        self._text_f.pack_propagate(False)

        self._name_l = Label(master=self._text_f, text=self.filename, font=(15), foreground='blue')
        self._name_l.bind('<ButtonRelease-1>', self.openfile)
        self._intros = f'''来自 :{fromuser}:{fromport}  \n分享代码 :{code} \n大小 :{sizetransform(size)}''' + f'''\n位置 :{location}'''
        self._intro_l = Label(master=self._text_f, text=self._intros)

        self._button_f = Frame(master=self._main_f, style='default.TFrame')
        self._begin_b = Button(master=self._button_f, image=iconmap['DOWNLOAD'], command=NULL)
        self._opencata_b = Button(master=self._button_f, image=iconmap['FOLDER'], command=self.openfiledir)
        self._del_b = Button(master=self._button_f, image=iconmap['DELETE'], command=NULL)

        self._pro_f = Frame(master=self.frame,)
        self._pro_l = Label(master=self._pro_f, text='请稍候...')
        self._probar = ProcessBar(master=self._pro_f, height=3)

        self.dlthread = threading.Thread(target=self.download, daemon=True)
        self.dlevent = threading.Event()
        self.dlbegin(NULL)
        self.state='wait'

    def __setattr__(self, __name: str, __value) -> None:
        if __name == 'process':
            self.setpro(__value)
        elif __name == 'state':
            self.setstate(__value)
        else:
            object.__setattr__(self,__name, __value)

    def pack(self):
        if self.img:
            self._img_l.pack(side=LEFT)
        self._name_l.pack(side=TOP, fill=X,)
        self._intro_l.pack(side=BOTTOM, fill=BOTH, expand=True)
        self._text_f.pack(side=LEFT)
        self._begin_b.pack(side=TOP)
        self._opencata_b.pack(side=TOP)
        self._del_b.pack(side=TOP)
        self._button_f.pack(side=RIGHT)
        self._text_f.pack(fill=BOTH, expand=True)
        
        self._main_f.pack(side=TOP, fill=X, expand=True, padx=2, pady=2)

        self._pro_l.pack(side=TOP, fill=X, expand=True)
        self._probar.pack(side=BOTTOM, fill=X, expand=True)
        self._pro_f.pack(side=BOTTOM, fill=X, padx=3, expand=True)

    def setstate(self, __value) -> None:
        
        if __value == 'error':
            self._pro_l.config(foreground='red', text='下载时发生异常')
            self._begin_b.config(state=NORMAL, image=iconmap['RETRY'])
            self._probar.setstyle('redf.TFrame')
            self._name_l.bind('<ButtonRelease-1>', NULL)
            self._name_l.config(foreground='gray')

        elif __value == 'wait':
            self._pro_l.config(foreground='black', text='请稍候...')
            self._begin_b.config(state=NORMAL, image=iconmap['DOWNLOAD'])
            self._probar.setstyle('bluef.TFrame')
            self._name_l.bind('<ButtonRelease-1>', NULL)
            self._name_l.config(foreground='gray')

        elif __value == 'complete':
            self._pro_l.config(foreground='green', text='下载完成')
            self._begin_b.config(state=NORMAL, image=iconmap['RETRY'])
            self._probar.setstyle('bluef.TFrame')
            self._name_l.bind('<ButtonRelease-1>', self.openfile)
            self._name_l.config(foreground='blue')

        elif __value == 'download':
            self._begin_b.config(state=DISABLED)
            self._probar.setstyle('bluef.TFrame')
            self._name_l.bind('<ButtonRelease-1>', NULL)
            self._name_l.config(foreground='gray')

        elif __value == 'interrupt':
            self.state = 'error'
            self._pro_l.config(text='Interrupted while downloading')
        else:
            raise TypeError('Bad state ' + str(__value))

    def setpro(self, proce:float) -> None:
        '''proce:float type,between 0.0-1.0'''
        if type(proce) != type(0.1) or proce < 0 or proce > 1:
            raise IndexError("proce can not be %s" % (str(proce)))
        self._pro_l.config(text='Downloading %d' % (proce * 100) + '%')
        self._probar.setpro(proce=proce)

    def openfile(self, *args):
        if args:
            logging.info('file open is called %s'%str(args))
        try:
            logging.debug(self.location + '''/''' + self.filename)
            open_file(self.location + '''/''' + self.filename)
        except FileNotFoundError:
            messagebox.showerror('错误！', '文件不存在\n可能因为文件已经移动')

    def dlbegin(self, func):  # @
        def tempfunc():
            func()
            self.dlevent.clear()
            self.state = 'download'
            self.dlthread = threading.Thread(target=self.download, daemon=True)
            self.dlthread.start()

        self.dlfunc = tempfunc
        self._begin_b.config(command=tempfunc)
        return func

    def openfiledir(self) -> None:
        if not os.path.isdir(self.location):
            messagebox.showerror('错误！', '目录不存在!')
        open_folder(self.location)

    def delete(self, func):  # @

        def delfunc(self=self):
            self.dlevent.set()
            self.state = 'wait'
            func(self)

        self._del_b.config(command=delfunc)
        return func

    def download(self):
        self.state = 'download'
        try:
            name, size = swdlc.getfileinfo(self.fromip, self.fromport, self.code)[0:2]
            if name=='' and size=='':
                raise KeyboardInterrupt
        except (HTTPError,URLError,KeyboardInterrupt):
            messagebox.showerror('SWDChat','Not Found.')
            return
        if name != self.filename or size != self.size:
            self.filename, self.size = name, size
            self._intro_l.config(text=f'''来自 :{self.fromip}:{self.fromport}  \n代码 :{self.code} \n大小 :{sizetransform(size)}''' + f'''\n位置 :{self.location}''')
            self._name_l.config(text=self.filename)
            ans = messagebox.askokcancel('SWDChat', f'''File infomation has been changed.
Sure to continue?
Name:{name}
Size:{sizetransform(size)}''')
            if not ans:
                return

        def report(percent):
            if self.dlevent.is_set():
                logging.debug('An downloading is interrupted')
                raise KeyboardInterrupt
            if percent == 100:
                self.state = 'complete'
            self.setpro(percent / 100.0)
            return
        
        try:
            print('https://%s:%d/s/%s'
                        % (self.fromip, int(self.fromport), self.code),
                        None, report)
            swdlc.filedown('https://%s:%d/s/%s'
                        % (self.fromip, int(self.fromport), self.code),
                        None, report)
        except (HTTPError, URLError):
            self.setstate('error')
        except KeyboardInterrupt:
            self.state = 'interrupt'


class DownloadManageFrame(Frame):
    'To create a "create frame"'

    def __init__(self, *args, **kwargs) -> None:
        self.filelist = []
        # super
        Frame.__init__(self,*args, **kwargs)
        # top lable
        self._top_l = Label(text='DownloadManager.', master=self)
        # main scrolledtext
        self._main_s = ScrolledText(master=self)
        # new config area
        self._new_f = Frame(master=self, style='filelayout.TFrame')
        self._new_l = Label(master=self._new_f, text='新任务')
        self._newtop_f = Frame(master=self._new_f)
        self._newbot_f = Frame(master=self._new_f)
        self._ip_e = Entry(master=self._newtop_f)
        self._port_e = Entry(master=self._newtop_f, width=7)
        self._code_e = Entry(master=self._newbot_f)
        self._ip_l = Label(master=self._newtop_f, text='IP')
        self._port_l = Label(master=self._newtop_f, text='PORT')
        self._code_l = Label(master=self._newbot_f, text='代码')
        self._adddl_b = Button(master=self._newtop_f, image=iconmap['DOWNLOAD'], command=self.adddl)
        self._add_b = Button(master=self._newbot_f, image=iconmap['ADD'], command=self.add)
        # Window arrange ends
        self._count_user = 0

    def __del__(self) -> None:
        'Warn not to delete the frame'
        logging.warning('An DownloadManageFrame is deleted!')
    
    def __setattr__(self, __name: str, __value: Any) -> None:
        return super().__setattr__(__name, __value)

    def pack(self, packframe:bool=False, *args, **kwargs):
        
        # Window arrange
        self._top_l.pack(side='top', fill='x')
        self._main_s.pack(side='top', fill='both', expand=True)

        self._ip_l.pack(side=LEFT,)
        self._ip_e.pack(side=LEFT, after=self._ip_l, fill=X, expand=True)
        self._port_l.pack(side=LEFT, after=self._ip_e,)
        self._port_e.pack(side=LEFT, after=self._port_l,)
        self._adddl_b.pack(side=LEFT, after=self._port_e)

        self._code_l.pack(side=LEFT,)
        self._code_e.pack(side=LEFT, after=self._code_l, fill=X, expand=True)
        self._add_b.pack(side=LEFT, after=self._code_e)

        self._new_l.pack(fill=X, expand=True, side=TOP, padx=2, pady=2)
        self._newtop_f.pack(fill=X, expand=True, side=TOP, padx=2, after=self._new_l)
        self._newbot_f.pack(fill=X, expand=True, side=BOTTOM, padx=2, pady=2)
        self._new_f.pack(fill=X, side=BOTTOM, after=self._top_l,)
        if packframe:
            super().pack(*args, **kwargs)

    def add(self):
        'add an new user'
        code = self._code_e.get()
        user = self._ip_e.get()
        port = self._port_e.get()
        self._code_e.delete(0, END)
        self._ip_e.delete(0, END)
        self._port_e.delete(0, END)
        ip, port = ipfill(user, port)
        try:
            port=int(port)
        except ValueError:
            messagebox.showerror('SWDChat','Bad Port')
            return
        return self.add_file(
                 code=code, fromuser=ip, fromport=int(port),
                 )

    def add_file(self,
                 code:str=None, fromuser:str=None,
                 fromport:int=None,) -> None:
        location = swdlc.downpath()
        try:
            print(fromuser, fromport, code)
            filename, filesize = swdlc.getfileinfo(fromuser, fromport, code)[0:2]
            if not filename and not filesize :
                raise FileNotFoundError
            print('aaaa', filename, filesize, type(filename))
        except (HTTPError, URLError, FileNotFoundError):
            messagebox.showerror('SWDChat', 'Not Found.')
            return 0
        
        def dele(self,tag:str=str(self._count_user), master=self._main_s, 
                 uslist:list=self.filelist):
            master.config(state='normal')
            master.delete(master.tag_ranges(tag)[0], master.tag_ranges(tag)[1])
            print(uslist)
            uslist.remove(self)
            master.config(state='disabled')

        newframe = FileFrame(master=self._main_s, width=int(self._main_s.winfo_width() - 5),
                           filename=filename, size=filesize,
                           location=location,
                           fromport=fromport, fromuser=fromuser,
                           code=code, img=getimg(filename))
        newframe.delete(dele)
        self.filelist.append(newframe)
        self._main_s.config(state='normal')
        newframe.pack()
        self._main_s.window_create(END, window=newframe.frame)
        self._main_s.insert(END,'\n',)
        self._main_s.tag_add(str(self._count_user),float(len(self.filelist)), 
                             float(len(self.filelist) + 1))
        self._count_user+=1
        self._main_s.config(state='disabled')
        return 1

    def adddl(self):
        if self.add():
            print('a')
            self.filelist[-1].dlfunc()


class ShareFrame(object):
    '''the frame that showcase a shareing file '''
    def __init__(self, master, width:int=None,
                 filename:str=None,
                 location:str=None, size:int=0,
                 code:str=None,
                 img:PhotoImage=None) -> None:
        self.frame = Frame(master=master, style='filelayout.TFrame', width=width, height=160)
        self.frame.pack_propagate(False)
        self.master = master
        self.bg = ''
        self.img = img
        self.location = location
        self.filename = filename
        self.size = size
        self.code = code

        self._main_f = Frame(master=self.frame)
        if self.img:
            self._img_l = Label(master=self._main_f, image=img)

        self._text_f = Frame(master=self._main_f,width=width-400 if width>400 else 200)
        self._text_f.pack_propagate(False)

        self._name_l = Label(master=self._text_f, text=self.filename, font=(15), foreground='blue')
        self._name_l.bind('<ButtonRelease-1>', self.openfile)
        self._intros = f'''分享代码 :{code} \n大小 :{sizetransform(size)}''' + f'''\n位置 :{location}'''
        self._intro_l = Label(master=self._text_f, text=self._intros)#width-400 if width>400 else 200)
        self._intro_l.pack_propagate(False)

        self._button_f = Frame(master=self._main_f, style='default.TFrame')
        self._opencata_b = Button(master=self._button_f, image=iconmap['FOLDER'], command=self.openfiledir)
        self._del_b = Button(master=self._button_f, image=iconmap['DELETE'], command=NULL)
        #Share it!
        swdlc.share(code=self.code,filepath=self.location+'/'+self.filename)


    def pack(self):
        if self.img:
            self._img_l.pack(side=LEFT)
        self._name_l.pack(side=TOP, fill=X,)
        self._intro_l.pack(side=BOTTOM, fill=Y, expand=True)
        self._text_f.pack(side=LEFT)
        self._opencata_b.pack(side=TOP)
        self._del_b.pack(side=TOP)
        self._button_f.pack(side=RIGHT)
        self._text_f.pack(fill=BOTH, expand=True)
        
        self._main_f.pack(side=TOP, fill=X, expand=True, padx=2, pady=2)

    def openfile(self, *args):
        if args:
            logging.info('file open is called' + str(args))
        try:
            logging.debug(self.location + '''/''' + self.filename)
            open_file(self.location + '''/''' + self.filename)
        except FileNotFoundError:
            messagebox.showerror('错误！', '文件不存在\n可能因为文件已经移动')

    def openfiledir(self) -> None:
        if not os.path.isdir(self.location):
            messagebox.showerror('错误！', '目录不存在!')
        open_folder(self.location)

    def delete(self, func):  

        def delfunc(self=self):
            swdlc.rmshare(self.code)
            func(self)

        self._del_b.config(command=delfunc)
        return func
    
    def config(self,nfilename:str,nfilepath:str,nsize:str,img:PhotoImage=None):
        self.filename=nfilename
        self.location=nfilepath
        self.size=nsize
        self.img=img
        if self.img:
            self._img_l.configure(image=img)
        self._name_l.configure(text=self.filename,)
        self._intros = f'''代码 :{self.code} \n大小 :{sizetransform(self.size)}''' + f'''\n位置 :{self.location}'''
        self._intro_l.configure(text=self._intros)
        swdlc.rmshare(code=self.code)
        swdlc.share(code=self.code,filepath=self.location + '''/''' + self.filename)



class ShareManageFrame(Frame):
    'To create a "SHare frame"'

    def __init__(self, *args, **kwargs) -> None:
        self.filelist = []
        # super
        Frame.__init__(self,*args, **kwargs)
        # top lable
        self._top_l = Label(text='ShareManage.', master=self)
        # main scrolledtext
        self._main_s = ScrolledText(master=self)
        # new config area
        self._new_f = Frame(master=self, style='filelayout.TFrame')
        self._new_l = Label(master=self._new_f, text='新任务')
        self._newtop_f = Frame(master=self._new_f)
        self._newbot_f = Frame(master=self._new_f)
        self._file_e = Label(self._newtop_f, background='white')
        self._code_e = Entry(master=self._newbot_f)
        self._file_l = Label(master=self._newtop_f, text='file')
        self._code_l = Label(master=self._newbot_f, text='代码')
        self._fileset_b = Button(master=self._newtop_f, image=iconmap['FOLDER'], command=self.chosefile)
        self._add_b = Button(master=self._newbot_f, image=iconmap['CONFIRM'], command=self.add)
        # Window arrange ends
        self._count_user = 0

    def __del__(self) -> None:
        'Warn not to delete the frame'
        logging.warning('An FileManageFrame is deleted!')
    
    def __setattr__(self, __name: str, __value: Any) -> None:
        return super().__setattr__(__name, __value)

    def pack(self, packframe:bool=False, *args, **kwargs):
        
        # Window arrange
        self._top_l.pack(side='top', fill='x')
        self._main_s.pack(side='top', fill='both', expand=True)

        self._file_l.pack(side=LEFT,)
        self._file_e.pack(side=LEFT, fill=X, expand=True)
        self._fileset_b.pack(side=LEFT, after=self._file_e)

        self._code_l.pack(side=LEFT,)
        self._code_e.pack(side=LEFT, after=self._code_l, fill=X, expand=True)
        self._add_b.pack(side=LEFT, after=self._code_e)

        self._new_l.pack(fill=X, expand=True, side=TOP, padx=2, pady=2)
        self._newtop_f.pack(fill=X, expand=True, side=TOP, padx=2, after=self._new_l)
        self._newbot_f.pack(fill=X, expand=True, side=BOTTOM, padx=2, pady=2)
        self._new_f.pack(fill=X, side=BOTTOM, after=self._top_l,)
        if packframe:
            super().pack(*args, **kwargs)

    
    def _setpath(self):  # 设定
        self._file_e['text'] = filedialog.askopenfilename()

    
    def chosefile(self):  # 设定分享文件
        self.sdfth = threading.Thread(daemon=True, target=self._setpath)
        self.sdfth.start()

    def add(self):
        'add an new file'
        code = self._code_e.get()
        file = self._file_e['text']
        if code.strip() == '' or not os.path.isfile(file) :
            messagebox.showerror('SWDChat','Bad code or file.')
            return
        self._code_e.delete(0, END)
        self._file_e.config(text='')
        return self.add_file(code=code,file=file)

    def add_file(self,
                 code:str=None, file:str=None,) -> None:
        '''add a file to list. Can also use in program'''
        def dele(self,tag:str=str(self._count_user), master=self._main_s, uslist:list=self.filelist):
            master.config(state='normal')
            master.delete(master.tag_ranges(tag)[0], master.tag_ranges(tag)[1])
            print(uslist)
            uslist.remove(self)
            master.config(state='disabled')
        filesize=os.path.getsize(file)
        location,filename=os.path.split(file)
        for i in self.filelist: #检查是否有重复的code
            if i.code == code:
                i.config(filename,location,filesize,getimg(filename=filename))
                return 'I do not know what to return :-('
        newframe = ShareFrame(master=self._main_s, width=int(self._main_s.winfo_width() - 5),
                           filename=filename, size=filesize,
                           location=location,
                           code=code, img=getimg(filename))
        newframe.delete(dele)
        self.filelist.append(newframe)
        self._main_s.config(state='normal')
        newframe.pack()
        self._main_s.window_create(END, window=newframe.frame)
        self._main_s.insert(END,'\n',)
        self._main_s.tag_add(str(self._count_user),float(len(self.filelist)), float(len(self.filelist) + 1))
        self._count_user+=1
        self._main_s.config(state='disabled')
        return 1



def init():
    global MYIP,MYPORT
    MYIP = swdlc.getip()
    MYPORT = swdlc.httpd.server_port  # @UndefinedVariable


def _demo():
    swdlc.init()
    swdlc.downpath('D:/')
    init()
    print(MYPORT)
    demotk = Toplevel()
    demotk.geometry('%dx%d' % (509*2, 652))
    b = ShareManageFrame(master=demotk)
    b.pack(packframe=True, side=LEFT, fill=Y, expand=True)
    c = DownloadManageFrame(master=demotk)
    c.pack(packframe=True, side=RIGHT, fill=Y, expand=True)
    # b=ShareFrame(master=demotk,filename='Settings.ini',
    #              img=PhotoImage(file='./icons/files/ini.png'),
    #              location='C:/',width=500)
    # b.delete(lambda *args:print('fffffff'))
    # b.pack()
    # b.frame.pack()
    demotk.mainloop()
    
    
if __name__ == '__main__':
    _demo()
