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
print('请稍后...')
import swdlc as lc
from swdlc import getip
import schat
import httpsserver as hs
from tkinter import *
from tkinter.scrolledtext import ScrolledText as ST
from tkinter.ttk import *
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
#以ID为键
un={}#user name
uf={}#user frame
ust={}#user ST
uso={}#user Schat object
f2id={}#str(frame):id
port=36144
iport=port-1
imgs=deque()#imgs
version='2.0.0a2'
if lc.getip()=='127.0.0.1':
    print('程序无法启动,请检查网络连接.')
    system('pause>nul')
if schat.init(port):
    schat.init(0)
port=schat.myport#本机使用的端口(int)
system('mkdir img>nul')
mw=Tk()#main window
mw.title('SWDChat %s'%version)
mw.iconbitmap('logo.ico')
mw.update()
mw.geometry('1100x700')
mw.resizable(0,0)
style1=Style()
style1.configure('my1.TNotebook', tabposition='n')
msg_f=Frame(mw,relief='ridge',borderwidth=1)
style2=Style()
style2.configure('my.TNotebook', tabposition='wn')
user_n=Notebook(msg_f,style='my.TNotebook')#user notebook
blank_l=Label(msg_f)
blank_l.pack(fill=X)
username_l=Label(msg_f,text='用户名：%s'%schat.username)
username_l.pack(fill=X)

#about_f
about_f=Frame(msg_f)
about_s=ST(about_f)
about_s.pack(fill=BOTH,expand=True)
about_s.tag_config('about',font=('Consolas',14))
about_s.insert(1.0,'''\
Welcome to SWDChat {v}

SWDChat {v} Copyright（C）2020-2024 SWD Studio

This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome redistribute it under certain conditions.
See the GNU General Public License for more details.

You can contact us on swd-go.ys168.com.
'''.format(v=version),'about')
about_s.config(state='disabled')
user_n.add(about_f,text='{:>12}'.format('关于'))
#about_f end

#set_f
set_f=Frame(msg_f)
myip_l=Label(set_f,text='本机IP:%s\n本机端口:%d'%(getip(),port))
myip_l.pack()

name_f=Frame(set_f)
name_l=Label(name_f,text='用户名:')
name_l.pack(side='left')
name_e=Entry(name_f)
name_e.pack(side='right',ipadx=85)
name_f.pack()

path_f=Frame(set_f)
path_l=Label(path_f,text='下载路径:')
path_l.pack(side='left')
path_e=Entry(path_f,state='disabled')
path_e.pack(side='right',ipadx=85)
path_f.pack()

def setpath():
    path_e.config(state='normal')
    path_e.delete(0,'end')
    path_e.insert(0,filedialog.askdirectory())
    path_e.config(state='disabled')
def sdf():
    sdfth=Thread(daemon=True,target=setpath)
    sdfth.start()
path_b=Button(set_f,text='设置下载路径',command=sdf)
path_b.pack()

def setting():
    schat.username=name_e.get()
    username_l.config(text='用户名：'+schat.username)
set_b=Button(set_f,text='保存设置',command=setting)
set_b.pack()
user_n.add(set_f,text='{:>12}'.format('设置'))
#set_f end

#new_f
new_f=Frame(msg_f)

newname_f=Frame(new_f)
newname_f.pack()
newname_l=Label(new_f,text='名称:')
newname_l.pack()
newname_e=Entry(new_f)
newname_e.pack()

new_s=ST(new_f)
new_s.pack(fill=X)

newhelp_b=Button(new_f,text='帮助',command=lambda:showinfo('SWDChat',
    '''格式：
用户1IP 用户1端口
用户2IP 用户2端口
...
端口可不填，不填则与本机端口一致
IP可以只填后缀，其余部分与本机一致
例如:(假设本机IP为192.168.101.1，端口为36144)
16 36145
0 16
那么这个群组会加入
192.168.101.16的36145端口的程序
192.168.0.16的36144端口的程序
以及当前程序
注：可在设置里查看本机IP和端口
'''))
newhelp_b.pack()
def new():
    newn=newname_e.get()
    if not newn:
        return
    if ' ' in newn:
        showerror('SWDChat','名称中不能有空格')
        return
    if newn in uso:
        showerror('SWDChat','该群组已存在')
        return
    userinfo=new_s.get(1.0,'end')
    t=[(getip(),port)]
    for i in userinfo.split('\n'):
        k=i.split()
        try:
            uport=int(k[1])
        except Exception:
            uport=port
        try:
            l=k[0].count('.')
        except IndexError:
            continue
        temp=getip().split('.')[:3-l]
        temp.append(k[0])
        ip='.'.join(temp)
        t.append((ip,uport),)
    frm=cteframe(t)
    uso[f2id[str(frm)]].name=newn
    for ip,mport in t:
        Thread(target=lc.send,
            args=(
                {'username':schat.username,'type':'new','addr':t,'name':newn,'chatid':f2id[str(frm)]},
                ip,str(mport))).start()
    user_n.insert(2,frm,
                text='{:>14}'.format(newn))
    newname_e.delete(0, 'end')
    new_s.delete(1.0, 'end')
    showinfo('SWDChat','创建成功')
    user_n.select(frm)
new_b=Button(new_f,text='提交',command=new)
new_b.pack()
user_n.add(new_f,text='{:>12}'.format('创建'))
#new_f end

whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)
showinfodll=ctypes.WinDLL('./showinfo.dll')
info=showinfodll.info

def cteframe(addr,chatid=None):
    try:
        return uf[chatid]
    except Exception:
        pass
    msgs=schat.SchatFrame(mw,address=tuple(map(tuple,addr)))
    msgs.mainloop()
    if chatid!=None:
        msgs.chatid=chatid
    else:
        chatid=msgs.chatid
    msgf=uf[chatid]=msgs.cw
    f2id[str(msgf)]=chatid
    mtext=ust[chatid]=msgs.mtext
    uso[chatid]=msgs
    mtext.tag_config('red',foreground='red')
    mtext.tag_config('black',foreground='black')
    return msgf
def sharedown(filename:str,url:str,path:str):
    #print('fd',path)
    if path[0]=='/':
        path='.'+path
    def downth():
        pb=Progressbar(sw)
        pb.pack()
        def report(percent):
            pb['value']=percent
            if percent==100:
                showinfo('SWDChat','下载完成')
                sw.destroy()
        try:
            lc.filedown(url,path,report)
        except (HTTPError,URLError) as e:
            le=Label(sw,text=e)
            le.pack()
    sw=Tk()
    sw.title('文件下载')
    sw.update()
    sw.attributes('-topmost',1)
    l=Label(sw,text='文件名:%s'%filename)
    l.pack()
    downth()
    sw.mainloop()
@lc.receive
def receive(obj):
    color='black'
    time=schat.gettime()
    user_n.insert(2,frm:=cteframe(obj['addr'],obj['chatid']),
               text='{:>14}'.format(obj['name']))
    uso[f2id[str(frm)]].name=obj['name']
    #print(obj,schat.username)
    mtext=ust[obj['chatid']]
    if obj['username']!=schat.username:
        sth=Thread(daemon=True,target=info,args=(
            ctypes.c_char_p(('新消息(来自 %s)'%obj['name']).encode('ANSI')),))
        sth.start()
    mtext.config(state='normal')
    if obj['type']=='img':#用'img'表示图片
        imgname=obj['imgname']
        path='.\\img\\'+imgname
        try:
            p=PhotoImage(file=path)
        except Exception:
            lc.filedown(obj['url'],path)
            p=PhotoImage(file=path)
        mtext.insert('1.0','\n')
        mtext.image_create(1.0,image=p)
        imgs.append(p)
        s=('[%s] %s\n'%
            (obj['username'],time)).replace('..','.')
        uso[obj['chatid']].receive(s,obj['username'])
    elif obj['type']=='file':#用'file'表示文件
        filename=obj['filename']
        def _downbf(*a):
            sharedown(filename,obj['url'],path_e.get()+'/'+filename)
        fb=Button(uf[obj['chatid']],text='下载 %s'%filename,command=_downbf)
        mtext.insert(1.0,'\n')
        mtext.window_create('1.0',window=fb)
        s=('[%s] %s\n'%
            (obj['username'],time)).replace('..','.')
        uso[obj['chatid']].receive(s,obj['username'])
    elif obj['type']=='msg':
        s=('[%s] %s\n%s\n'%
            (obj['username'],time,obj['msg'])).replace('..','.')
        uso[obj['chatid']].receive(s,obj['username'])
    elif obj['type']=='new':#用2表示创建新群组
        pass
    else:
        color='red'
        s=('[%s] %s\n%s\n'%
            (obj['username'],time,'当前SWDChat版本过低，无法查看此消息。')).replace('..','.')
        mtext.insert(1.0,s,color)
    mtext.config(state='disabled')
    index=user_n.index('current')
    st=user_n.tab(index)
    st=st['text'].split()[-1]
    if st!=obj['name']:
        c=user_n.tab(uf[obj['chatid']],'text')
        user_n.tab(uf[obj['chatid']],text=c.replace('    ','  ! ',1))
def ntd(*a):
    index=user_n.index('current')
    st=user_n.tab(index)
    st=st['text'].split()[-1]
    fstr=user_n.tabs()[index]
    if st in ('关于','设置','创建'):
        if st=='设置':
            name_e.delete(0,'end')
            name_e.insert(0,schat.username)
        return
    c=user_n.tab(uf[f2id[fstr]],'text')
    user_n.tab(uf[f2id[fstr]],text=c.replace('!',' ',1))
def enter(*a):
    index=user_n.index('current')
    st=user_n.tab(index)
    fstr=user_n.tabs()[index]
    st=st['text'].split()[-1]
    if st in ('关于','设置','创建'):
        return
    uso[f2id[fstr]].click()
mw.bind("<Return>",enter)
mw.bind("<<NotebookTabChanged>> ",ntd)
user_n.add(about_f,text='{:>12}'.format('关于'))
user_n.add(t:=Frame())
user_n.hide(t)
user_n.pack(fill=BOTH,expand=True)
msg_f.pack(fill=BOTH,expand=True)
myip=lc.getip()
mainloop()
