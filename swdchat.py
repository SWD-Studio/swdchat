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

from sys import exit
import ctypes
from threading import Thread
from os import system
from urllib.error import HTTPError,URLError
from collections import deque
from tkinter import *
import tkinter.filedialog as filedialog
from tkinter.scrolledtext import ScrolledText as ST
from tkinter.ttk import *
from tkinter.messagebox import showerror,showinfo

import swdlc as lc
from swdlc import getip
import schat
import create
#以chatid为键
un={}#chatid:用户名
uf={}#chatid:Frame
ust={}#chatid:ST
uso={}#chatid:Schat对象
#以str(frame)为键
f2id={}#str(frame):chatid

port=36144#首选端口
imgs=deque()#存放PhotoImage对象
version='2.0.0a3'#版本号
if lc.getip()=='127.0.0.1':#若未连接互联网，地址应为127.0.0.1
    print('程序无法启动,请检查网络连接.')
    system('pause>nul')
if schat.init(port):#36144已被占用
    schat.init(0)#使用随机端口
port=schat.myport#本机使用的端口(int)
system('mkdir img>>nul')#创建img文件夹
mw=Tk()#SWDChat主窗口
mw.title('SWDChat %s'%version)#设定标题
mw.iconbitmap('logo.ico')#设定图标
mw.update()#刷新窗口
mw.geometry('1100x700')#设定窗口大小
mw.resizable(0,0)#窗口大小不可修改
style1=Style()#设定选项卡方向
style1.configure('my1.TNotebook', tabposition='n')
msg_f=Frame(mw,relief='ridge',borderwidth=1)#SWDChat根Frame对象
style2=Style()#设定选项卡方向
style2.configure('my.TNotebook', tabposition='wn')
user_n=Notebook(msg_f,style='my.TNotebook')#左侧选项卡
blank_l=Label(msg_f)#空白标签，置于窗口最上方
blank_l.pack(fill=X)
username_l=Label(msg_f,text='用户名：%s'%schat.username)#用户名标签
username_l.pack(fill=X)


#about_f 关于（首页）
about_f=Frame(msg_f)
about_s=ST(about_f)
about_s.pack(fill=BOTH,expand=True)
about_s.tag_config('about',font=('Consolas',14))#设置字体
about_s.insert(1.0,'''\
Welcome to SWDChat {v}

SWDChat {v} Copyright（C）2020-2024 SWD Studio

This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome redistribute it under certain conditions.
See the GNU General Public License for more details.

You can contact us on swd-go.ys168.com.
'''.format(v=version),'about')
about_s.config(state='disabled')
user_n.add(about_f,text='{:>12}'.format('关于'))#添加到选项卡
#about_f end

#set_f 设置
set_f=Frame(msg_f)
myip_l=Label(set_f,text='本机IP:%s\n本机端口:%d'%(getip(),port))#IP及端口信息
myip_l.pack()

name_f=Frame(set_f)#用户名设定
name_l=Label(name_f,text='用户名:')
name_l.pack(side='left')
name_e=Entry(name_f)
name_e.pack(side='right',ipadx=85)
name_f.pack()

path_f=Frame(set_f)#下载路径设定
path_l=Label(path_f,text='下载路径:')
path_l.pack(side='left')
path_e=Entry(path_f,state='disabled')
path_e.pack(side='right',ipadx=85)
path_f.pack()

def setpath():#设定下载路径线程
    path_e.config(state='normal')
    path_e.insert(0,filedialog.askdirectory())
    path_e.delete(0,'end')
    path_e.config(state='disabled')
def sdf():#设定下载路径
    sdfth=Thread(daemon=True,target=setpath)
    sdfth.start()
path_b=Button(set_f,text='设置下载路径',command=sdf)
path_b.pack()

def setting():#保存设置
    schat.username=name_e.get()
    username_l.config(text='用户名：'+schat.username)
set_b=Button(set_f,text='保存设置',command=setting)
set_b.pack()
user_n.add(set_f,text='{:>12}'.format('设置'))#添加到选项卡
#set_f end

#new_f
create.ipconfig(ip=lc.getip(),port=port)
new_f=create.CreateFrame(master=msg_f)
@new_f.fetch
def new(newn,userset):#创建新群组
    #newn=newname_e.get()#获得群组名称

    if newn in uso:#已存在
        showerror('SWDChat','该群组已存在')
        return
    t=[]
    for k in userset:
        try:
            uport=int(k[1])
        except Exception:#若端口留空则用本机端口
            uport=port
        try:#数IP的后缀数
            l=k[0].count('.')
        except IndexError:
            continue
        temp=getip().split('.')[:3-l]#加上各段IP
        temp.append(k[0])
        ip='.'.join(temp)
        t.append((ip,uport),)#加入用户信息
    frm=cteframe(t)#创建新Frame、Schat对象等
    uso[f2id[str(frm)]].name=newn#修改群组名
    for ip,mport in t:#向各用户发送创建新群组
        Thread(target=lc.send,
            args=(
                {'username':schat.username,'type':'new','addr':t,'name':newn,'chatid':f2id[str(frm)]},
                ip,str(mport))).start()#使用多线程
    user_n.insert(2,frm,
                text='{:>14}'.format(newn))#添加到选项卡
    #newname_e.delete(0, 'end')#清空
    #new_s.delete(1.0, 'end')
    user_n.select(frm)#打开新创建的群组
#new_b.pack()
user_n.add(new_f.frame,text='{:>12}'.format('创建'))#添加到选项卡
#new_f end

#隐藏命令行窗口
whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)
#加载动态链接库
showinfodll=ctypes.WinDLL('./showinfo.dll')
info=showinfodll.info

def cteframe(addr,chatid=None):#创建新Frame、Schat对象等
    try:#若群组已经创建
        return uf[chatid]#直接返回
    except Exception:
        pass
    msgs=schat.SchatFrame(mw,address=tuple(map(tuple,addr)))#创建新对象
    msgs.mainloop()#加载控件
    if chatid!=None:#代表该群组已存在，但本机首次收到消息
        msgs.chatid=chatid#覆盖自动生成的chatid
    else:#创建新的群组
        chatid=msgs.chatid#记录新的chatid
    #记录该群组有关对象
    msgf=uf[chatid]=msgs.cw
    f2id[str(msgf)]=chatid
    mtext=ust[chatid]=msgs.mtext
    uso[chatid]=msgs
    mtext.tag_config('red',foreground='red')#配置聊天消息颜色
    mtext.tag_config('black',foreground='black')
    return msgf#返回Frame对象
def sharedown(filename:str,url:str,path:str):#下载分享文件
    #print('fd',path)
    if path[0]=='/':#未设置默认路径
        path='.'+path#把当前路径作为默认路径
    def downth():#处理下载操作
        pb=Progressbar(sw)
        pb.pack()
        def report(percent):#回调函数，修改进度条
            pb['value']=percent
            if percent==100:
                showinfo('SWDChat','下载完成')
                sw.destroy()
        try:#下载
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
def receive(obj):#接收消息
    color='black'#默认颜色
    time=schat.gettime()#获取当前时间
    user_n.insert(2,frm:=cteframe(obj['addr'],obj['chatid']),
               text='{:>14}'.format(obj['name']))#把当前群组移到第一个
    uso[f2id[str(frm)]].name=obj['name']#修改群组名称(若该群组对象已存在则无实际作用)
    #print(obj,schat.username)
    mtext=ust[obj['chatid']]#获取当前群组对应的文本框
    if obj['username']!=schat.username:#收到其他用户发来的消息
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
    elif obj['type']=='msg':#用'msg'表示文字消息
        s=('[%s] %s\n%s\n'%
            (obj['username'],time,obj['msg'])).replace('..','.')
        uso[obj['chatid']].receive(s,obj['username'])
    elif obj['type']=='new':#用'new'表示创建新群组，或成员修改
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
    if st!=obj['name']:#有新消息的群组不处于选中状态
        c=user_n.tab(uf[obj['chatid']],'text')
        user_n.tab(uf[obj['chatid']],text=c.replace('    ','  ! ',1))#添加一个'!'提示
def ntd(*a):#处理选项卡单击事件
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
def enter(*a):#处理回车键事件(调用'发送'按钮)
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
user_n.pack(fill=BOTH,expand=True)
msg_f.pack(fill=BOTH,expand=True)
myip=lc.getip()
mainloop()
