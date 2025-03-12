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
#    You can contact us on swd-go.ys168.com.

from tkinter import *  # @UnusedWildImport
from tkinter.ttk import *  # @UnusedWildImport
mw = Tk()  # SWDChat主窗口
mw.withdraw()
import ui_snapshot

# 隐藏命令行窗口
import ctypes
import platform
if platform.system()=="Windows":
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        ctypes.windll.kernel32.CloseHandle(whnd)

from threading import Thread
from os import system
from urllib.error import HTTPError, URLError
from collections import deque
from tkinter.messagebox import askyesnocancel, showerror, showinfo, askokcancel
from time import time
from json import dumps, loads
from os.path import expandvars
import webbrowser

import pystray
from PIL import Image  # @Reimport

import swdlc as lc
from swdlc import getip
import ui_voicerec
import schat
import ui_groupset
import ui_aboutf
import ui_mainsetf
import scwidgets
import filemanager
import multiplatform

# 系统托盘


def _quit():             # 自定义回调函数
    icon.stop()                        # 对象停止方法
    mw.quit()
    mw.destroy()


def hide_window(*args):
    mw.withdraw()
    if not hidewindowdefault:
        icon.notify('窗口已隐藏到托盘区', 'SWDChat')


# 创建图标对象
icon_image = Image.open("logo.ico")           # 打开 ICO 图像文件并创建一个 Image 对象
menu = (pystray.MenuItem(text='打开窗口', action=mw.deiconify, default=True),
        pystray.Menu.SEPARATOR, 
        pystray.MenuItem(text='退出', action=_quit))  # 创建菜单项元组
# 创建 PyStray Icon 对象，并传入关键参数
icon = pystray.Icon("swdchat", icon_image, "SWDChat", menu)

# 显示图标
# 启动托盘图标目录
icon_thread = Thread(target=icon.run, daemon=True)
icon_thread.start()
info = icon.notify

# loop_thread = Thread(target=mw.mainloop,daemon=True)

# 以chatid为键
un = {}  # chatid:用户名
uf = {}  # chatid:Frame
ust = {}  # chatid:ST
uso = {}  # chatid:Schat对象

# 以str(frame)为键
f2id = {}  # str(frame):chatid

port = 36144  # 首选端口
imgs = deque()  # 存放PhotoImage对象
version = '2.2.0'  # 版本号
if lc.getip() == '127.0.0.1':  # 若未连接互联网，地址应为127.0.0.1
    print('程序无法启动,请检查网络连接.')
    system('pause>>nul')
if schat.init(port):  # 首选端口已被占用
    schat.init(0)  # 使用随机端口
port = schat.myport  # 本机使用的端口(int)
hidewindowdefault=None

class Recdict(object):
    flag = 0

    def __init__(self, dictobj):
        self.dict = dictobj

    def __getitem__(self, key):
        if key in self.dict:
            return self.dict[key]
        else:
            self.flag = 1
            return ''

    def __setitem__(self, key, val):
        self.dict[key] = val

    def __repr__(self):
        return repr(self.dict)

    @property
    def isErr(self):
        return self.flag


ui_groupset.ipconfig(ip=lc.getip(), port=port)
ui_aboutf.config(vers=version)
ui_mainsetf.ipconfig(ip=lc.getip(), port=port)
ui_mainsetf.config(version)
system('mkdir img>>nul')  # 创建img文件夹
mw.title('SWDChat %s' % version)  # 设定标题
mw.iconbitmap('logo.ico')  # 设定图标
mw.update()  # 刷新窗口
mw.geometry('800x500')  # 设定窗口大小
mw.resizable(0, 0)  # 窗口大小不可修改
style1 = Style()  # 设定选项卡方向
style1.configure('my1.TNotebook', tabposition='n')
msg_f = Frame(mw, relief='ridge', borderwidth=1)  # SWDChat根Frame对象
style2 = Style()  # 设定选项卡方向
style2.configure('my.TNotebook', tabposition='wn')
user_n = Notebook(msg_f, style='my.TNotebook')  # 左侧选项卡
blank_l = Label(msg_f)  # 空白标签，置于窗口最上方
blank_l.pack(fill=X)
username_l = Label(msg_f, text='用户名：%s' % schat.username)  # 用户名标签
username_l.pack(fill=X)
temp_userlist = []

# set_f 设置
set_f = ui_mainsetf.MainSetFrame(username=schat.username)
set_f.pack()
def quitfunc():
    icon.stop()
    mw.destroy()
set_f.del_b.config(command=quitfunc)


@set_f.setting
def setting():  # 保存设置 @UnusedVariable
    global hidewindowdefault
    schat.username = set_f.username
    if not set_f.default_path:
        set_f.default_path = '.'
    lc.downpath(set_f.default_path)
    hidewindowdefault=set_f.del_option_v
    set_dict={'username':set_f.username, 'path':set_f.default_path, 'del_option':hidewindowdefault}
    system(f'echo {dumps(set_dict)}>{cache_path}\\set.dat')
    username_l.config(text='用户名：' + schat.username)

# set_f end


# new_f
new_f = ui_groupset.GroupSetFrame(master=msg_f)


@new_f.fetch
def new(newn, userlist):  # 创建新群组
    # newn=newname_e.get()#获得群组名称
    t = userlist
    print('userlist:', t)
    if newn in uso:  # 已存在
        showerror('SWDChat', '该群组已存在')
        return
    frm = cteframe(t)  # 创建新Frame、Schat对象等
    so = uso[f2id[str(frm)]]
    so.name = newn  # 修改群组名
    so.name_l.config(text=newn)
    so.sendnew()  # 向各用户发送创建新群组
    bakobj = so.sendnew(False)
    print('new dump',dumps(bakobj,ensure_ascii=False))
    system('echo {}>>{}\\bak.dat'.format(dumps(bakobj,ensure_ascii=False),cache_path))
    user_n.insert(2, frm,
                  text='{:>14}'.format(newn))  # 添加到选项卡
    # newname_e.delete(0, 'end')#清空
    # new_s.delete(1.0, 'end')
    user_n.select(frm)  # 打开新创建的群组


# new_b.pack()
# new_f end

# modify_f
modify_id = -1.0  # 当前正修改的chatid
modify_f = ui_groupset.GroupSetFrame(master=msg_f, method=ui_groupset.CONFIG)

# file manager
filemanager.init()
lc.downpath('.')
filedw=filemanager.DownloadManageFrame()
filesh=filemanager.ShareManageFrame()
filedw.pack(False)
filesh.pack(False)
# file manager end

@modify_f.fetch
def modify(name, userlist):
    if modify_id == -1.0:
        user_n.hide(modify_f.frame)
        return
    # user_n.hide(modify_f.frame)
    user_n.select(uf[modify_id])
    so = uso[modify_id]
    so.name = name
    so.name_l.config(text=name)
    so.address = userlist
    so.addrver = str(time())
    so.sendnew()
    newmsg = so.sendnew(False)
    print(temp_userlist, userlist)
    for i in temp_userlist:
        if i not in userlist:
            Thread(target=lc.send,
                   args=(newmsg, *i)).start()
# end modify

about_f = ui_aboutf.AboutFrame()
#--------------注册按钮--------------

about_f.btns['new']=Button(master=about_f.frame,width=15,text='新建会话',command=lambda : user_n.select(new_f.frame))
about_f.btns['newfile']=Button(master=about_f.frame,width=15,text='新建文件分享',command=lambda : user_n.select(filesh))
about_f.btns['learn']=Button(master=about_f.frame,width=15,text='查看文档',command=lambda : multiplatform.open_file('./HELP.html'))
about_f.btns['surf']=Button(master=about_f.frame,width=15,text='访问我们的主页',command=lambda : webbrowser.open(url='https://github.com/SWD-Studio/swdchat',new=2))
about_f.pack()


def cteframe(addr, addrver='0', chatid=None, obj=None):  # 创建新Frame、Schat对象等
    if chatid in uso:  # 若群组已经创建
        return uf[chatid]
    msgs = schat.SchatFrame(mw, address=list(map(list, addr)))  # 创建新对象
    if obj != None:
        bakobj = obj.dict
        bakobj['type'] = 'new'
        print('457',dumps(bakobj,ensure_ascii=False))
        system('echo {}>>{}\\bak.dat'.format(dumps(bakobj,ensure_ascii=False),cache_path))
    
    def _modify(self):
        global modify_id, temp_userlist
        modify_id = self.chatid
        userlist = list(self.address)
        for i in range(len(userlist)):
            userlist[i] = {'ip': userlist[i][0],
                           'port': userlist[i][1],
                           'username': self.usernames['{}:{}'.format(*userlist[i])],
                           }
        temp_userlist = self.address[:]
        modify_f.initsets(msgs.name, userlist)
        modify_f.reset()

        def _cancel(*a):  # @UnusedVariable
            ans = askokcancel('提示', '确定要删除该群组记录吗？')
            if ans:
                user_n.forget(uf[self.chatid])
                delobj=uso[self.chatid].sendnew(False)
                delobj['type']='del'
                delobj['addrver']=str(time())
                system('echo {}>>{}\\bak.dat'.format(dumps(delobj, ensure_ascii=False), cache_path))
                # user_n.hide(modify_f.frame)
                user_n.select(about_f.frame)

        modify_f.cancel(_cancel)
        user_n.select(modify_f.frame)

    msgs.modify = _modify
    # 用于记录用户名，"IP:port":用户名
    msgs.usernames = Recdict({'{}:{}'.format(*a): '' for a in addr})
    msgs.mainloop()  # 加载控件
    if chatid != None:  # 代表该群组已存在，但本机首次收到消息
        msgs.chatid = chatid  # 覆盖自动生成的chatid
    else:  # 创建新的群组
        chatid = msgs.chatid  # 记录新的chatid
    if addrver != '0':
        msgs.addrver = addrver
    # 记录该群组有关对象
    msgf = uf[chatid] = msgs.cw
    f2id[str(msgf)] = chatid
    mtext = ust[chatid] = msgs.mtext
    uso[chatid] = msgs
    mtext.tag_config('red', foreground='red')  # 配置聊天消息颜色
    mtext.tag_config('black', foreground='black')
    return msgf  # 返回Frame对象


def sharedown(filename: str, url: str, path: str):  # 下载分享文件
    print('fd',path)
    if path[0] == '/':  # 未设置默认路径
        path = '.' + path  # 把当前路径作为默认路径

    def downth():  # 处理下载操作
        pb = Progressbar(sw)
        pb.pack()

        def report(percent):  # 回调函数，修改进度条
            pb['value'] = percent
            if percent == 100:
                showinfo('SWDChat', '下载完成')
                sw.destroy()

        try:  # 下载
            lc.filedown(url, path, report)
        except (HTTPError, URLError) as e:
            le = Label(sw, text=e)
            le.pack()

    sw = Tk()
    sw.title('文件下载')
    sw.update()
    sw.attributes('-topmost', 1)
    l = Label(sw, text='文件名:%s' % filename)
    l.pack()
    t = Thread(target=downth)
    t.start()
    sw.mainloop()


@lc.receive
def receive(obj):  # 接收消息
    obj = Recdict(obj)
    print('receive:', obj)
    frm = cteframe(obj['addr'], obj['addrver'], obj['chatid'], obj)
    from_ = obj['from']
    so = uso[f2id[str(frm)]]  # 当前SchatFrame对象
    flag = False
    if so.addrver < obj['addrver']:  # 更新用户列表
        flag = True
        so.addrver = obj['addrver']
        so.address = obj['addr']
        if [lc.getip(), port] not in so.address and (lc.getip(), port) not in so.address:
            so.disabled = True
            for i in so.buttons:
                so.buttons[i].config(state='disabled')
        else:
            so.disabled = False
            for i in so.buttons:
                so.buttons[i].config(state='normal')
    if from_:
        fromaddr = from_.split(':')
        fromaddr[1] = int(fromaddr[1])
        if fromaddr not in so.address:
            Thread(target=lc.send,
                   args=(uso[obj['chatid']].sendnew(False), *obj['from'].split(':'))).start()
            return
    if obj['chatid'] in uso and obj['addrver'] < uso[obj['chatid']].addrver:
        uso[obj['chatid']].sendnew()
        Thread(target=lc.send,
               args=(uso[obj['chatid']].sendnew(False), *obj['from'].split(':'))).start()
    color = 'black'  # 默认颜色
    nowtime = schat.gettime()  # 获取当前时间
    user_n.insert(1, frm, text='{:>14}'.format(obj['name']))  # 把当前群组移到第一个
    so.name_l.config(text=obj['name'])
    so.name = obj['name']  # 修改群组名称(若该群组对象已存在则无实际作用)
    so.usernames[from_] = obj['username']
    print(obj.dict, '\n', so.usernames)
    mtext = ust[obj['chatid']]  # 获取当前群组对应的文本框
    if from_ != '{}:{}'.format(getip(), port):  # 收到其他用户发来的消息
        color = 'blue'
        sth = Thread(daemon=True, target=info, args=(
            'SWDChat', ('新消息(来自 %s)' % obj['name'])),)
        sth.start()
    s = '[%s] %s  From: %s' % (obj['username'], nowtime, from_)
    if obj.isErr:
        s += '    (此消息来自旧版SWDChat，部分内容可能未正确显示。)'
    s += '\n'
    mtext.config(state='normal')
    if obj['type'] == 'new' or flag:  # 成员修改
        userlist = list(so.address)
        for i in range(len(userlist)):
            userlist[i] = '{}:{}'.format(*userlist[i])
        color = 'orange'
        mtext.insert(1.0,
                     '当前成员列表：\n[IP:端口号,用户名]\n' + str(['{}\",\"{}'.format(j, so.usernames[j]) for j in userlist]) + '\n', color)
    if obj['type'] == 'new':  # 用'new'表示创建新群组，或成员修改
        pass
    elif obj['type'] == 'img':  # 用'img'表示图片
        imgname = obj['imgname']
        path = '.\\img\\' + imgname
        try:
            if lc.calcsha256(path) != obj['sha256']:
                raise FileNotFoundError
        except Exception:
            lc.filedown(obj['url'], path)
        p = scwidgets.ImageDisplayLabel(img_path=path,width=400,height=400)
        mtext.insert('1.0', '\n')
        mtext.window_create(1.0, window=p)
        imgs.append(p)
    elif obj['type'] == 'file':  # 用'file'表示文件
        filename = obj['filename']

        def _downbf(*a):  # @UnusedVariable
            sharedown(filename, obj['url'],
                      filename)

        fb = Button(uf[obj['chatid']], text='下载 %s' %
                    filename, command=_downbf)
        mtext.insert(1.0, '\n')
        mtext.window_create('1.0', window=fb)
    elif obj['type'] == 'msg':  # 用'msg'表示文本消息
        s += obj['msg']
    else:
        color = 'red'
        s += '当前SWDChat版本过低，无法查看此消息。\n'
    mtext.insert(1.0, s, color)
    mtext.config(state='disabled')
    index = user_n.index('current')
    st = user_n.tab(index)
    st = st['text'].split()[-1]
    if st != obj['name']:  # 有新消息的群组不处于选中状态
        c = user_n.tab(uf[obj['chatid']], 'text')
        if '!' not in c:
            user_n.tab(uf[obj['chatid']], text=c.replace(
                '    ', '  ! ', 1))  # 添加一个'!'提示


config_tabs = ('关于', '设置', '创建', '修改', '文件下载', '文件分享')


def ntd(*a):  # 处理选项卡单击事件 @UnusedVariable
    
    index = user_n.index('current')
    st = user_n.tab(index)
    st = st['text'].split()[-1]
    if st != '修改':
        user_n.hide(modify_f.frame)
    fstr = user_n.tabs()[index]
    if st in config_tabs:
        if st == '设置':
            set_f.reset()
        return
    
    # def _voice(self):
    #     ui_voicerec.voicetoplevel.target=self.msg
    
    c = user_n.tab(uf[f2id[fstr]], 'text')
    user_n.tab(uf[f2id[fstr]], text=c.replace('!', ' ', 1))


def get_current_chatid():  # 获取当前chatid
    index = user_n.index('current')
    st = user_n.tab(index)
    fstr = user_n.tabs()[index]
    st = st['text'].split()[-1]
    if st in config_tabs:
        return ''
    return f2id[fstr]


def voice():
    chatid=get_current_chatid()
    if chatid:
        so=uso[chatid]
        return so.msg
ui_voicerec.voicetoplevel.get_current_msg=voice
ui_voicerec.voicetoplevel.pack()
ui_voicerec.voicetoplevel.withdraw()

user_n.add(about_f.frame, text='{:>12}'.format('关于'))  # 添加到选项卡
user_n.add(set_f.frame, text='{:>12}'.format('设置'))  # 添加到选项卡
user_n.insert(1, new_f.frame, text='{:>12}'.format('创建'))  # 添加到选项卡
user_n.insert(1, modify_f.frame, text='{:>12}'.format('修改'))  # 添加到选项卡
user_n.hide(modify_f.frame)
user_n.insert(1, filedw, text='{:>12}'.format('文件下载'))  # 添加到选项卡
user_n.insert(1, filesh, text='{:>12}'.format('文件分享'))  # 添加到选项卡

cache_path='%appdata%\\SWD\\SWDChat\\chat2'
try:
    system(f'mkdir {cache_path}>>nul')  # 创建缓存文件夹
    fp=open(expandvars(f'{cache_path}\\set.dat'))
    set_dict=loads(fp.readline())
    set_f.setup(**set_dict)
    setting()
except Exception as e:
    print('settings bak exception:', type(e), e)
    system(f'del {cache_path}\\set.dat  /F /Q')

try:
    system(f'copy {cache_path}\\bak.dat _bak1')
    f = open('_bak1')
    t = {}
    for i in f.readlines():
        try:
            obj = loads(i)
        except Exception as e:
            print(type(e),e)
            continue
        print('bakobj:', obj)
        if [lc.getip(), port] not in obj['addr']:
            continue
        if obj['chatid'] not in t or 'addrver' not in t[obj['chatid']]:
            t[obj['chatid']] = obj
        elif obj['addrver'] > t[obj['chatid']]['addrver']:
            t[obj['chatid']] = obj
    for i in t:
        if t[i]['type']!='del':
            receive(t[i])
    system(f'del {cache_path}\\bak.dat /F /Q')
    for i in t:
        if t[i]['type']!='del':
            system('echo {}>>{}\\bak.dat'.format(dumps(t[i],ensure_ascii=False),cache_path))
    f.close()
    system('del _bak1 /F /Q')
except Exception as e:
    print('groups bak exception:', type(e), e)
    system(f'del {cache_path}\\bak.dat  /F /Q')
    system(f'del _bak1  /F /Q')
# mw.bind("<Return>", enter)
mw.bind("<<NotebookTabChanged>> ", ntd)
user_n.add(about_f.frame, text='{:>12}'.format('关于'))
user_n.pack(fill=BOTH, expand=True)
msg_f.pack(fill=BOTH, expand=True)
myip = lc.getip()
def unmap_switch(*args):
    global hidewindowdefault
    if hidewindowdefault==None:
        hidewindowdefault=askyesnocancel("SWDChat","您是否希望将窗口隐藏到托盘区？\n如果关闭窗口,您会收不到之后收到的消息")
    if hidewindowdefault==None:
        return
    if hidewindowdefault:
        hide_window()
    else:
        icon.stop()
        mw.destroy()
# mw.bind("<Unmap>", hide_window)
ui_snapshot.delete()

mw.protocol("WM_DELETE_WINDOW", unmap_switch)
mw.deiconify()
mainloop()
