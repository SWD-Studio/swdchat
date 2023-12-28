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
import os
from time import sleep,localtime, strftime
from urllib.parse import quote
from urllib.error import HTTPError,URLError
from collections import deque
uf={}#user frame
ust={}#user ST
port=36144
imgs=deque()#imgs
version='1.1.0rc3'
if lc.getip()=='127.0.0.1':
    print('程序无法启动,请检查网络连接.')
    system('pause>nul')
if lc.init(port):
    print('端口被占用,程序无法启动.')
    system('pause>nul')
mw=Tk()#main window
mw.title('SWDChat %s'%version)
mw.update()
mw.geometry('400x650')
#mw.resizable(0,0)
style1=Style()
style1.configure('my1.TNotebook', tabposition='n')
mn=Notebook(mw,style='my1.TNotebook')#main notebook
w=Frame(mw,relief='ridge',borderwidth=1)
fw=Frame(mw,relief='ridge',borderwidth=1)#file window
style2=Style()
style2.configure('my.TNotebook', tabposition='wn')
umn=Notebook(w,style='my.TNotebook')#user msg notebook
aboutf=Frame(w)
aboutmt=ST(aboutf)
aboutmt.tag_config('red',foreground='red')
msgf=Frame(w)
fpa=Frame(w)
fda=Frame(w)
fsend=Frame(w)
isend=Frame(w)#image
pa=Entry(fpa)
da=Entry(fda)
msg=Entry(fsend)
fdp=Frame(fw)
ldp=Label(fdp,text='下载路径:')
edp=Entry(fdp,state='disabled')
lpa=Label(fpa,text='IP前缀:')
lda=Label(fda,text='用户IP后缀:')
share=ST(fw,state='disabled')
whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)
showinfo=ctypes.WinDLL('./showinfo.dll')
info=showinfo.info
def gettime():
    t=strftime("%X", localtime())
    return t[:t.rfind(':')]
def cteframe(da):
    try:
        return uf[str(da)]
    except Exception:
        pass
    msgf=uf[str(da)]=Frame(w)
    mtext=ust[str(da)]=ST(msgf,state='disabled')
    mtext.tag_config('blue',foreground='blue')#received
    mtext.pack(fill=BOTH,expand=True)
    return msgf
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
        s=('[%s] %s\n%s\n'
            %(lc.getip()[plen+1:],gettime(),s)).replace('..','.')
        umn.insert(1,cteframe(da.get()),
                   text='{:>14}'.format(da.get()))
        mtext=ust[da.get()]
        mtext.config(state='normal')
        mtext.insert(1.0,s)
        mtext.config(state='disabled')
        msg.delete(0,'end')
        umn.select(uf[da.get()])
    except Exception as e:
        showerror('ERROR',e)
def setpath():
    lc.downpath(filedialog.askdirectory())
    edp.config(state='normal')
    edp.delete(0,'end')
    edp.insert(0,lc.downpath())
    edp.config(state='disabled')
def sendimg():
    if pa.get()=='' or da.get()=='' or sic.get()=='':
        return
    umn.insert(1,cteframe(da.get()),
                   text='{:>14}'.format(da.get()))
    umn.select(uf[da.get()])
    plen=len(pa.get())
    mtext=ust[da.get()]
    path='./img/%s'%sic.get()
    p=PhotoImage(file=path)
    mtext.config(state='normal')
    mtext.insert('1.0','\n')
    mtext.image_create(1.0,image=p)
    imgs.append(p)
    s=('[%s] %s\n'%
            (lc.getip()[plen+1:],gettime())).replace('..','.')
    mtext.insert('1.0',s)
    mtext.config(state='disabled')
    lc.send((lc.getip(),1,sic.get()),(pa.get()+'.'+da.get()).replace('..','.'),str(port))
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
    time=gettime()
    plen=len(pa.get())
    umn.insert(1,cteframe(obj[0][plen+1:]),
               text='{:>14}'.format(obj[0][plen+1:]))
    print(len('{:>14}'.format(obj[0][plen+1:])))
    mtext=ust[obj[0][plen+1:]]
    sth=Thread(daemon=True,target=info,args=(
        ctypes.c_char_p(('新消息(来自 %s)'%obj[0][plen+1:]).encode('ANSI')),))
    sth.start()
    mtext.config(state='normal')
    if obj[1]==1:#用1表示图片
        path='./img/%s'%obj[2]
        p=PhotoImage(file=path)
        mtext.insert('1.0','\n')
        mtext.image_create(1.0,image=p)
        imgs.append(p)
        s=('[%s] %s\n'%
            (obj[0][plen+1:],time)).replace('..','.')
    else:
        s=('[%s] %s\n%s\n'%
            (obj[0][plen+1:],time,obj[1])).replace('..','.')
    mtext.insert('1.0',s,'blue')
    mtext.config(state='disabled')
    index=umn.index('current')
    st=umn.tab(index)
    st=st['text'].split()[-1]
    if st!=obj[0][plen+1:] and obj[0][plen+1:]!=lc.getip()[plen+1:]:
        c=umn.tab(uf[obj[0][plen+1:]],'text')
        umn.tab(uf[obj[0][plen+1:]],text=c.replace('    ','  ! ',1))
b=Button(fsend,text='发送',command=click)
sic=Combobox(isend)
sic['values']=[str(i).split('\'')[1] for i in os.scandir(path='./img')]
sib=Button(isend,text='发送图片',command=sendimg)
sharef=Frame(fw)
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
bf=Button(fw,text='设置下载路径',command=sdf)
def ntd(*a):
    index=umn.index('current')
    st=umn.tab(index)
    st=st['text'].split()[-1]
    if st=='关于':return
    c=umn.tab(uf[st],'text')
    umn.tab(uf[st],text=c.replace('!',' ',1))
    da.delete(0,'end')
    da.insert(0,st)
mw.bind("<Return>",click)
mw.bind("<<NotebookTabChanged>> ",ntd)
Label(w).pack()#empty labels
Label(fw).pack()
lpa.pack(side='left')
pa.pack(side='right')
fpa.pack()
lda.pack(side='left')
da.pack(side='right')
fda.pack()
msg.pack(side='left',ipadx=70)
b.pack(side='right')
fsend.pack()
sic.pack(side='left')
sib.pack(side='right')
isend.pack()
ldp.pack(side='left')
edp.pack(side='right',ipadx=85)
fdp.pack()
bf.pack()
bs.pack(side='left')
bd.pack(side='right')
sharef.pack()
aboutmt.pack(fill=BOTH,expand=True)
share.pack(fill=BOTH,expand=True)
mn.add(w,text='    消息    ')
mn.add(fw,text='    文件    ')
umn.add(aboutf,text='{:>12}'.format('关于'))
umn.add(t:=Frame())
umn.hide(t)
mn.pack(fill=BOTH,expand=True)
umn.pack(fill=BOTH,expand=True)
aboutmt.insert(1.0,'''\
继续使用本程序即表明您已阅读并接受GNU通用公共许可协议
SWDChat %s，
版权所有（C）2020-2023 SWD Coding Group
    本程序在适用法律范围内不提供品质担保。除非另作书面声明，版权持有人及其他程序提供者“概”不提供任何显式或隐式的品质担保，品质担保所指包括而不仅限于有经济价值和适合特定用途的保证。全部风险，如程序的质量和性能问题，皆由你承担。若程序出现缺陷，你将承担所有必要的修复和更正服务的费用。
    除非适用法律或书面协议要求，任何版权持有人或本程序按本协议可能存在的第三方修改和再发布者，都不对你的损失负有责任，包括由于使用或者不能使用本程序造成的任何一般的、特殊的、偶发的或重大的损失（包括而不仅限于数据丢失、数据失真、你或第三方的后续损失、其他程序无法与本程序协同运作），即使那些人声称会对此负责。
See the GNU General Public License for more details.
'''%version)
aboutmt.insert('end','\n本机IP:%s'%lc.getip(),'red')
aboutmt.config(state='disabled')
share.config(state='normal')
share.insert(1.0,'''\
文件分享列表:
分享代码\文件路径''')
share.config(state='disabled')
myip=lc.getip()
pa.insert(0,'.'.join(myip.split('.')[:3]))
mainloop()
