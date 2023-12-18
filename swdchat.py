#    Copyright (C) 2020-2023  SWD Code Group

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
#    You can contact us on swd-go.yespan.com.
print('请稍后...')
import swdlc as lc
from tkinter import *
from tkinter.scrolledtext import ScrolledText as ST
from tkinter.ttk import *
from tkinter import filedialog
from tkinter.messagebox import showerror,showinfo
from sys import exit
import ctypes
from threading import Thread
from multiprocessing import Process
from os import system
from time import sleep
from urllib.parse import quote
from urllib.error import HTTPError,URLError
from collections import deque
um={}#user msg
ul=set()#userlist
port=36144
version='1.1.0rc1'
if lc.getip()=='127.0.0.1':
    print('程序无法启动,请检查网络连接.')
    system('pause>nul')
if lc.init(port):
    print('端口被占用,程序无法启动.')
    system('pause>nul')
w=Tk()
w.title('SWDChat %s'%version)
w.update()
w.geometry('400x650')
fpa=Frame(w)
fda=Frame(w)
fsend=Frame(w)
pa=Entry(fpa)
da=Combobox(fda)
da['value']=()
msg=Entry(fsend)
fdp=Frame(w)
ldp=Label(fdp,text='下载路径:')
edp=Entry(fdp,state='disabled')
mtext=ST(w,state='disabled')
mtext.tag_config('orange',foreground='orange')#default_user
mtext.tag_config('blue',foreground='blue')#received
mtext.tag_config('red',foreground='red')
lpa=Label(fpa,text='IP前缀:')
lda=Label(fda,text='用户IP后缀:')
share=ST(w,state='disabled')
whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)
showinfo=ctypes.WinDLL('./showinfo.dll')
info=showinfo.info
def opensharewin():
    def destroy():
        fmap=lc.fmap
        share.config(state='normal')
        share.delete(3.0,'end')
        share.insert(3.0,'\n')
        for i in fmap:
            share.insert('end','{} {}\n'.format(i,fmap[i]))
        share.config(state='disabled')
        sw.destroy()
    def fileselect():
        fn=filedialog.askopenfilename()
        if fn=='':
            return
        ep.delete(0,'end')
        ep.insert(0,fn)
    def submit(*a):
        if ec.get()=='' or ep.get()=='':
            return
        lc.share(ec.get(),ep.get())
        destroy()
    def rmsf():
        if ec.get()=='':
            return
        lc.rmshare(ec.get())
        destroy()
    sw=Tk()
    sw.bind("<Return>",submit)
    sw.title('文件分享')
    sw.update()
    sw.attributes('-topmost',1)
    fcode=Frame(sw)
    fpath=Frame(sw)
    of=Button(sw,text='打开文件',command=fileselect)
    sub=Button(sw,text='提交',command=submit)
    rms=Button(sw,text='删除分享',command=rmsf)
    lco=Label(fcode,text='分享代码:')
    lp=Label(fpath,text='文件路径:')
    ec=Entry(fcode)
    ep=Entry(fpath)
    lco.pack(side='left')
    ec.pack(side='right')
    fcode.pack()
    lp.pack(side='left')
    ep.pack(side='right')
    fpath.pack()
    of.pack()
    sub.pack()
    rms.pack()
    sw.mainloop()
def click(*a):
    try:
        s=msg.get()
        if s=='' or da.get=='':
            return
        sendmsg(s,da.get())
        plen=len(pa.get())
        s=('[%s->%s]%s\n'
            %(lc.getip()[plen+1:],da.get(),s)).replace('..','.')
        if da.get() not in ul:
            um[da.get()]=[s,]
            ul.add(da.get())
            da['value']=tuple(ul)
        else:
            um[da.get()].append(s)
        msg.delete(0,'end')
        csd()
    except Exception as e:
        showerror('ERROR',e)
def setpath():
    lc.downpath(filedialog.askdirectory())
    edp.config(state='normal')
    edp.delete(0,'end')
    edp.insert(0,lc.downpath())
    edp.config(state='disabled')
def sendmsg(s,no):
    if pa.get()=='' or no=='':
        raise SyntaxError
    lc.send((lc.getip(),s),(pa.get()+'.'+no).replace('..','.'),str(port))
    plen=len(pa.get())
def sharedown():
    def downth():
        pb=Progressbar(sw)
        pb.pack()
        def report(percent):
            pb['value']=percent
            if percent==100:
                sw.destroy()
        try:
            lc.filedown('https://%s:%d/s/%s'
                        %((pa.get()+'.'+ep.get()).replace('..','.'),port,
                          quote(ec.get())),
                        None,report)
        except (HTTPError,URLError) as e:
            le=Label(sw,text=e)
            le.pack()
    def submit(*a):
        global sw
        sub.config(state='disabled')
        ec.config(state='disabled')
        ep.config(state='disabled')
        if ec.get()=='' or ep.get()=='':
            return
        fdown=Thread(daemon=True,target=downth)
        fdown.start()
    sw=Tk()
    sw.title('文件下载')
    sw.update()
    sw.bind("<Return>",submit)
    sw.attributes('-topmost',1)
    fcode=Frame(sw)
    fpath=Frame(sw)
    sub=Button(sw,text='提交',command=submit)
    lco=Label(fcode,text='分享代码:')
    lp=Label(fpath,text='IP后缀:')
    ec=Entry(fcode)
    ep=Entry(fpath)
    ep.insert(0,da.get())
    lco.pack(side='left')
    ec.pack(side='right')
    lp.pack(side='left')
    ep.pack(side='right')
    fpath.pack()
    fcode.pack()
    sub.pack()
    sw.mainloop()
@lc.receive
def receive(obj):
    sth=Thread(daemon=True,target=info)
    sth.start()
    plen=len(pa.get())
    s=('[%s->%s]%s\n'%
        (obj[0][plen+1:],lc.getip()[plen+1:],obj[1])).replace('..','.')
    if obj[0][plen+1:] not in ul:
        um[obj[0][plen+1:]]=[s,]
        ul.add(obj[0][plen+1:])
        da['value']=tuple(ul)
    else:
        um[obj[0][plen+1:]].append(s)
    if da.get()==obj[0][plen+1:]:
        csd()
b=Button(fsend,text='发送',command=click)
sharef=Frame(w)
def osws():
    oswth=Thread(daemon=True,target=opensharewin)
    oswth.start()
bs=Button(sharef,text='文件分享',command=osws)
def sds():
    sdth=Process(daemon=True,target=sharedown)
    sdth.run()
bd=Button(sharef,text='文件下载',command=sds)
def sdf():
    sdfth=Thread(daemon=True,target=setpath)
    sdfth.start()
bf=Button(w,text='设置下载路径',command=sdf)
def csd(*a):
    un=da.get()
    plen=len(pa.get())
    mtext.config(state='normal')
    mtext.delete(1.0,'end')
    for i in um[un]:
        if i[1:i.find('->')]!=lc.getip()[plen+1:]:
            mtext.insert(1.0,i,'blue')
        else:
            mtext.insert(1.0,i)
    mtext.config(state='disabled')
w.bind("<Return>",click)
w.bind("<<ComboboxSelected>>",csd)
lpa.pack(side='left')
pa.pack(side='right')
fpa.pack()
lda.pack(side='left')
da.pack(side='right')
fda.pack()
msg.pack(side='left',ipadx=70)
b.pack(side='right')
fsend.pack()
ldp.pack(side='left')
edp.pack(side='right',ipadx=85)
fdp.pack()
bf.pack()
bs.pack(side='left')
bd.pack(side='right')
sharef.pack()
mtext.pack()
share.pack()
mtext.config(state='normal')
mtext.insert(1.0,'''\
继续使用本程序即表明您已阅读并接受GNU通用公共许可协议
SWDChat第%s版，
版权所有（C）2020-2023 SWD Coding Group
    本程序在适用法律范围内不提供品质担保。除非另作书面声明，版权持有人及其他程序提供者“概”不提供任何显式或隐式的品质担保，品质担保所指包括而不仅限于有经济价值和适合特定用途的保证。全部风险，如程序的质量和性能问题，皆由你承担。若程序出现缺陷，你将承担所有必要的修复和更正服务的费用。
    除非适用法律或书面协议要求，任何版权持有人或本程序按本协议可能存在的第三方修改和再发布者，都不对你的损失负有责任，包括由于使用或者不能使用本程序造成的任何一般的、特殊的、偶发的或重大的损失（包括而不仅限于数据丢失、数据失真、你或第三方的后续损失、其他程序无法与本程序协同运作），即使那些人声称会对此负责。
See the GNU General Public License for more details.
'''%version)
mtext.insert('end','\n本机IP:%s'%lc.getip(),'red')
mtext.config(state='disabled')
share.config(state='normal')
share.insert(1.0,'''\
文件分享列表:
分享代码\文件路径''')
share.config(state='disabled')
myip=lc.getip()
pa.insert(0,'.'.join(myip.split('.')[:3]))
mainloop()
