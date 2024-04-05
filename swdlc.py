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
#20240306
#是否启用TLS成为可选项
#默认端口改为随机
#注释
import socket
from json import dumps,loads
import os
import threading
import ssl
from http import HTTPStatus
import shutil
from urllib.request import urlopen,urlretrieve
from urllib.parse import quote,unquote
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http.client import BadStatusLine
from sys import stderr
from time import sleep

daddr=None#默认地址
ssl._create_default_https_context=ssl._create_unverified_context
#忽略ssl证书警告
myip=socket.gethostbyname(socket.gethostname())#获取本机IP地址
def getip():
    """获取本机IP地址
返回值为本机IP,str
"""
    return myip
class InvalidAddress(Exception):pass
fmap={}#记录本机分享代码对应的文件，格式为code:fpath
stimes={}#记录分享代码可用次数
class SHRH(BaseHTTPRequestHandler):
    """swdlc的主服务器
"""
    def do_GET(self):
        """处理文件下载操作
"""
        if self.path.startswith('/sdown/'):#文件下载请求(来自重定向)
            f=None#用于存储文件指针
            code=self.path.split('/')[2]#获取文件分享代码
            ucode=unquote(code)#从URL中重建原始分享代码(可能包含非ASCII字符)
            if ucode not in fmap:#检查分享代码是否存在
                self.send_error(HTTPStatus.NOT_FOUND,'Code not found.')
                return
            try:#尝试读取文件
                f=open(fmap[ucode],'rb')
                fs = os.fstat(f.fileno())
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-type", 'application/octet-stream')
                self.send_header("Content-Length", str(fs[6]))
                self.end_headers()
            except:
                self.send_error(HTTPStatus.NOT_FOUND,'File not found.')
                try:
                    f.close()
                except (UnboundLocalError,AttributeError):
                    pass
            if f:#如果正确读入文件，那么f不为None
                try:#把文件写入响应体
                    shutil.copyfileobj(f,self.wfile)
                    #print(fmap)
                    stimes[code]-=1
                    if stimes[code]==0:
                        del stimes[code]
                        del fmap[code]
                finally:
                    f.close()
        elif self.path.startswith('/getname/'):#获取文件名
            code=self.path.split('/')[2]
            ucode=unquote(code)
            if ucode not in fmap:
                self.send_error(HTTPStatus.NOT_FOUND,'Code not found.')
                return
            self.send_response(200)
            self.send_header(quote(fmap[ucode].split('/')[-1]), '')
            self.end_headers()
        elif self.path=='/favicon.ico' or self.path=='' or self.path[0:3]!='/s/':
            #忽略请求图标等
            self.send_response(200)
            self.end_headers()
            return
        elif self.path.startswith('/s/'):
            #文件下载(客户端发送)
            code=self.path.split('/')[2]
            ucode=unquote(code)
            if ucode not in fmap:
                self.send_error(HTTPStatus.NOT_FOUND,'File not Found')
                return
            self.send_response(HTTPStatus.FOUND)#重定向的响应码
            s='/sdown/%s/%s'%(ucode,fmap[ucode].split('/')[-1])#重定向地址
            s=quote(s)#编码为ASCII
            self.send_header("Location", s)
            self.end_headers()
    def do_POST(self):
        """接收Python对象(json)
"""
        clen=int(self.headers['Content-Length'])#POST长度
        try:
            body=self.rfile.read(clen)
            res=loads(body)#从json转换为Python对象
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'200 OK')
            receive_func(res)#调用用户设定的函数,传入收到的对象
        except Exception as e:
            print(e)
def default_addr(ip:str,port:str):
    """设定send函数默认发送地址，无返回值
格式：default_addr(ip:str, port:str)
"""
    global daddr
    daddr=prot+ip+':'+str(port)#拼接地址
def send(obj:object,ip:str=None,port:str=None,timeout:int=2):
    """发送可以被转换为json字符串的Python对象
格式：send(obj:onject, ip:str, port:str, timeout:int)
obj：要发送的对象
ip：发送到的IP地址
port：发送到的端口
timeout：超时时间，默认为2
ip, port若不填则使用default_addr设定的默认IP地址及端口
"""
    try:
        addr=prot+ip+':'+str(port)
    except Exception:#如果有变量为None，则使用默认地址
        addr=daddr
    if addr==None:
        raise InvalidAddress("地址无效")
    s=dumps(obj)#转换为json
    try:
        urlopen(addr,data=s.encode(),timeout=timeout)#发送对象
    except BadStatusLine as e:
        ...
        #print(e)
def receive(func):
    """装饰器，被装饰函数为收到Python对象时调用，会传入收到的对象
"""
    global receive_func
    receive_func=func
    return func
def downpath(path:str=None):
    """为filedown设定文件下载路径
"""
    global defpath
    if path is None:
        return defpath
    defpath=path
def filedown(url:str,file:str=None,report=None):
    """文件下载
格式：filedown(url:str, file:str, report=None)
从指定的URL下载文件，file为文件名
filedown(url:str,report=None)
用于swdlc的文件分享
url='https://<IP>:<port>/s/<sharecode>'
report为回调函数
"""
    def reporthook(blocknum,blocksize,totalsize):
        percent=int(100*blocknum*blocksize/totalsize)
        if percent>100:
            percent=100
        report(percent)
    if file==None:
        t=urlopen(url.replace('/s/','/getname/'))
        file=unquote(str(t.headers).split('\n')[2][:-2])
    try:
        file=(defpath+'/'+file).replace('//','/')
    except Exception:
        ...
    #print('swdlc',file)
    f,h=urlretrieve(url,file,reporthook=reporthook if report!=None else None)
    file=open(file)
    file.close()
def share(code:str,filepath:str,times:int=-1):
    """创建分享链接
code：分享代码
filepath：文件名(含路径)
times：允许下载次数(若输入小于零则无限次)
"""
    fmap[code]=filepath
    stimes[code]=times
def rmshare(code):
    """移除分享代码为code的链接(不删除文件)
返回值：
成功：0
找不到分享代码：1
"""
    try:
        del fmap[code]
    except Exception:#找不到分享代码
        return 1
    return 0
def init(port:int=0,daemon:bool=True,enable_TLS:bool=True):
    """初始化函数，应当在导入swdlc后立即调用
port：本机服务器端口，默认随机
daemon：设置服务器线程是否为守护线程
enable_TLS：设置服务器是否使用https
返回值：
正常：0
有误：1
"""
    global httpd
    global sport
    global prot
    prot='https://' if enable_TLS else 'http://'
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:#检测端口占用
        sock.bind((getip(),port))#若无法绑定则说明端口已被占用
    except OSError:
        return 1
    finally:
        sock.close()
    sock.close()
    port=int(port)
    sport=port
    httpd=ThreadingHTTPServer((getip(),port),SHRH)#创建服务器
    if enable_TLS:#套接字
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)#创建上下文
        context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')#证书
        httpd.socket=context.wrap_socket(httpd.socket,server_side=True)#修改套接字
    t=threading.Thread(daemon=daemon,target=httpd.serve_forever)#创建线程
    t.start()#启动线程
    return 0
if __name__=='__main__':
    if init(65140,False):
        print('端口已被占用')
        raise SystemExit
    default_addr(getip(),'65140')
    @receive#接收函数
    def receive(obj):
        print(obj)
    send(5)
