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

import ctypes
from threading import Thread
from os import system
from urllib.error import HTTPError,URLError
from collections import deque
from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import showerror,showinfo
from time import time

import swdlc as lc
from swdlc import getip
import schat
import ui_groupset
import ui_aboutf
import ui_mainsetf
#以chatid为键
un={}#chatid:用户名
uf={}#chatid:Frame
ust={}#chatid:ST
uso={}#chatid:Schat对象
#以str(frame)为键
f2id={}#str(frame):chatid

port=14364#首选端口
imgs=deque()#存放PhotoImage对象
version='2.0.0a3'#版本号
if lc.getip()=='127.0.0.1':#若未连接互联网，地址应为127.0.0.1
    print('程序无法启动,请检查网络连接.')
    system('pause>nul')
if schat.init(port):#36144已被占用
    schat.init(0)#使用随机端口
port=schat.myport#本机使用的端口(int)


class Recdict(object):
    flag=0
    def __init__(self,dictobj):
        self.dict=dictobj
    def __getitem__(self,key):
        if key in self.dict:
            return self.dict[key]
        else:
            self.flag=1
            return ''
    def __setitem__(self,key,val):
        self.dict[key]=val
    def __repr__(self):
        return repr(self.dict)
    @property
    def isErr(self):
        return self.flag

ui_groupset.ipconfig(ip=lc.getip(),port=port)
ui_aboutf.config(vers=version)
ui_mainsetf.ipconfig(ip=lc.getip(),port=port)

system('mkdir img>>nul')#创建img文件夹
mw=Tk()#SWDChat主窗口
mw.title('SWDChat %s'%version)#设定标题
mw.iconbitmap('logo.ico')#设定图标
mw.update()#刷新窗口
mw.geometry('1100x700')#设定窗口大小
#mw.resizable(0,0)#窗口大小不可修改
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


about_f=ui_aboutf.AboutFrame()
about_f.pack()
user_n.add(about_f.frame,text='{:>12}'.format('关于'))#添加到选项卡


#set_f 设置
set_f=ui_mainsetf.MainSetFrame(username=schat.username)
set_f.pack()

user_n.add(set_f.frame,text='{:>12}'.format('设置'))#添加到选项卡
@set_f.setting
def setting(name):#保存设置 
        schat.username=set_f.username
        username_l.config(text='用户名：'+schat.username)


#set_f end

#new_f
new_f=ui_groupset.GroupSetFrame(master=msg_f)
@new_f.fetch
def new(newn,userlist):#创建新群组
    #newn=newname_e.get()#获得群组名称
    t=userlist
       
    if newn in uso:#已存在
        showerror('SWDChat','该群组已存在')
        return
    frm=cteframe(t)#创建新Frame、Schat对象等
    so=uso[f2id[str(frm)]]
    so.name=newn#修改群组名
    so.sendnew()#向各用户发送创建新群组
    user_n.insert(2,frm,
                text='{:>14}'.format(newn))#添加到选项卡
    #newname_e.delete(0, 'end')#清空
    #new_s.delete(1.0, 'end')
    user_n.select(frm)#打开新创建的群组
#new_b.pack()
user_n.add(new_f.frame,text='{:>12}'.format('创建'))#添加到选项卡
#new_f end

#modify_f
modify_id=-1.0#当前正修改的chatid
modify_f=ui_groupset.GroupSetFrame(master=msg_f,method=ui_groupset.CONFIG)
user_n.insert(1,modify_f.frame,text='{:>12}'.format('修改'))#添加到选项卡
user_n.hide(modify_f.frame)
@modify_f.fetch
def modify(name,userlist):
    if modify_id==-1.0:
        user_n.hide(modify_f.frame)
        return
    user_n.hide(modify_f.frame)
    so=uso[modify_id]
    so.name=name
    print(userlist)
    so.address=userlist
    so.addrver=str(time())
    so.sendnew()
#end modify
#隐藏命令行窗口
whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)
#加载动态链接库
showinfodll=ctypes.WinDLL('./showinfo.dll')
info=showinfodll.info

def cteframe(addr,addrver=0,chatid=None):#创建新Frame、Schat对象等
    if chatid in uso:#若群组已经创建
        if uso[chatid].addrver>=addrver:#用户列表版本最新
            return uf[chatid]
        else:#更新用户列表
            so=uso[chatid]
            so.addver=addrver
            so.address=addr
            return uf[chatid]
    msgs=schat.SchatFrame(mw,address=tuple(map(tuple,addr)))#创建新对象
    def _modify(self):
        global modify_id
        modify_id=self.chatid
        userlist=self.address[:]
        for i in range(len(userlist)):
            userlist[i]={'ip':userlist[i][0],
                         'port':userlist[i][1],
                         'username':self.usernames['{}:{}'.format(*userlist[i])],
                         }
        print(userlist)
        modify_f.reset(clear=True)
        modify_f.initsets(msgs.name, userlist)
        modify_f.cancel(lambda *a:showinfo('SWDChat','请点击左侧其他任意选项卡以退出'))
        print(124678)
        user_n.select(modify_f.frame)
    msgs.modify=_modify
    msgs.usernames=Recdict({'{}:{}'.format(*a):'' for a in addr})#用于记录用户名，"IP:port":用户名
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
    obj=Recdict(obj)
    color='black'#默认颜色
    time=schat.gettime()#获取当前时间
    user_n.insert(2,frm:=cteframe(obj['addr'],obj['addrver'],obj['chatid']),
               text='{:>14}'.format(obj['name']))#把当前群组移到第一个
    from_=obj['from']
    so=uso[f2id[str(frm)]]#当前SchatFrame对象
    so.name=obj['name']#修改群组名称(若该群组对象已存在则无实际作用)
    so.usernames[from_]=obj['username']
    print(obj.dict,'\n',so.usernames)
    mtext=ust[obj['chatid']]#获取当前群组对应的文本框
    if from_!='{}:{}'.format(getip(),port):#收到其他用户发来的消息
        color='blue'
        sth=Thread(daemon=True,target=info,args=(
            ctypes.c_char_p(('新消息(来自 %s)'%obj['name']).encode('ANSI')),))
        sth.start()
    s='[%s] %s  From: %s'%(obj['username'],time,from_)
    if obj.isErr:
        s+='    (此消息来自旧版SWDChat，部分内容可能未正确显示。)'
    s+='\n'
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
    elif obj['type']=='file':#用'file'表示文件
        filename=obj['filename']
        def _downbf(*a):
            sharedown(filename,obj['url'],set_f.default_path+'/'+filename)
        fb=Button(uf[obj['chatid']],text='下载 %s'%filename,command=_downbf)
        mtext.insert(1.0,'\n')
        mtext.window_create('1.0',window=fb)
    elif obj['type']=='msg':#用'msg'表示文字消息
        s+=obj['msg']+'\n'
    elif obj['type']=='new':#用'new'表示创建新群组，或成员修改
        userlist=so.address[:]
        for i in range(len(userlist)):
            userlist[i]='{}:{}'.format(*userlist[i])
        color='orange'
        mtext.insert(1.0,
                     '当前成员列表：\n[IP:端口号,用户名]\n'+str(['{}\",\"{}'.format(i,so.usernames[i]) for i in userlist])+'\n'
                     ,color)
    else:
        color='red'
        s+='当前SWDChat版本过低，无法查看此消息。\n'
    mtext.insert(1.0,s,color)
    mtext.config(state='disabled')
    index=user_n.index('current')
    st=user_n.tab(index)
    st=st['text'].split()[-1]
    if st!=obj['name']:#有新消息的群组不处于选中状态
        c=user_n.tab(uf[obj['chatid']],'text')
        if '!' not in c:
            user_n.tab(uf[obj['chatid']],text=c.replace('    ','  ! ',1))#添加一个'!'提示
config_tabs=('关于','设置','创建','修改')
def ntd(*a):#处理选项卡单击事件
    index=user_n.index('current')
    st=user_n.tab(index)
    st=st['text'].split()[-1]
    if st!='修改':
        user_n.hide(modify_f.frame) 
    fstr=user_n.tabs()[index]
    if st in config_tabs:
        if st=='设置':
            set_f.reset()
        elif st=='创建':
            new_f.reset(clear=True)
        return
    c=user_n.tab(uf[f2id[fstr]],'text')
    user_n.tab(uf[f2id[fstr]],text=c.replace('!',' ',1))
def enter(*a):#处理回车键事件(调用'发送'按钮)
    index=user_n.index('current')
    st=user_n.tab(index)
    fstr=user_n.tabs()[index]
    st=st['text'].split()[-1]
    if st in config_tabs:
        return
    uso[f2id[fstr]].click()
mw.bind("<Return>",enter)
mw.bind("<<NotebookTabChanged>> ",ntd)
user_n.add(about_f.frame,text='{:>12}'.format('关于'))
user_n.pack(fill=BOTH,expand=True)
msg_f.pack(fill=BOTH,expand=True)
myip=lc.getip()
mainloop()
