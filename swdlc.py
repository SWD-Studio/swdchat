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
#    You can contact us on swd-go.ysepan.com.
# 20241220
# 添加响应头字段Sha256
# 添加检查：是否有文件跳跃攻击
import socket
import hashlib
from json import dumps, loads
import os
import threading
import ssl
from http import HTTPStatus
import shutil
from urllib.request import urlopen, urlretrieve, HTTPErrorProcessor
from urllib.parse import quote, unquote, urlparse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from sys import stderr
from time import sleep

daddr = None  # 默认地址
ssl._create_default_https_context = ssl._create_unverified_context
# 忽略ssl证书警告
myip = socket.gethostbyname(socket.gethostname())  # 获取本机IP地址
defpath = '.'


def getip():
    """获取本机IP地址
返回值为本机IP,str
"""
    return myip


class InvalidAddress(Exception):
    pass


fmap = {}  # 记录本机分享代码对应的文件，格式为code:fpath
stimes = {}  # 记录分享代码可用次数

http_response_backup = HTTPErrorProcessor.http_response


def http_response(self, request, response):  # 防止非2XX响应码报错 @UnusedVariable
    return response


HTTPErrorProcessor.http_response = http_response
HTTPErrorProcessor.https_response = http_response


def calcsha256(fpath: str)->str:
    print(fpath)
    with open(fpath, 'rb') as fp:
        fhash = hashlib.sha256()
        for chunk in iter(lambda: fp.read(4096), b''):
            fhash.update(chunk)
    return fhash.hexdigest()


class SHRH(BaseHTTPRequestHandler):
    """swdlc的主服务器
"""

    def do_GET(self):
        """处理文件下载操作
"""
        if self.path.startswith('/sdown/'):  # 文件下载请求(来自重定向)
            f = None  # 用于存储文件指针
            code = self.path.split('/')[2]  # 获取文件分享代码
            ucode = unquote(code)  # 从URL中重建原始分享代码(可能包含非ASCII字符)
            if ucode not in fmap:  # 检查分享代码是否存在
                self.send_error(HTTPStatus.NOT_FOUND, 'Code not found.')
                return
            try:  # 尝试读取文件
                f = open(fmap[ucode], 'rb')
                fs = os.fstat(f.fileno())
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-type", 'application/octet-stream')
                self.send_header("Content-Length", str(fs[6]))
                self.end_headers()
            except:
                self.send_error(HTTPStatus.NOT_FOUND, 'File not found.')
                try:
                    f.close()
                except (UnboundLocalError, AttributeError):
                    pass
            if f:  # 如果正确读入文件，那么f不为None
                try:  # 把文件写入响应体
                    shutil.copyfileobj(f, self.wfile)
                    # print(fmap)
                    stimes[code] -= 1
                    if stimes[code] == 0:
                        del stimes[code]
                        del fmap[code]
                finally:
                    f.close()
        elif self.path.startswith('/getname/'):  # 获取文件名（已弃用，用于兼容旧版）
            code = self.path.split('/')[2]
            ucode = unquote(code)
            if ucode not in fmap:
                self.send_error(HTTPStatus.NOT_FOUND, 'Code not found.')
                return
            self.send_response(200)
            self.send_header(quote(fmap[ucode].split('/')[-1]), '')
            self.end_headers()
        elif self.path.startswith('/fileinfo/'):  # 获取文件信息
            f = None  # 用于存储文件指针
            code = self.path.split('/')[2]  # 获取文件分享代码
            ucode = unquote(code)  # 从URL中重建原始分享代码(可能包含非ASCII字符)
            if ucode not in fmap:  # 检查分享代码是否存在
                self.send_error(HTTPStatus.NOT_FOUND, 'Code not found.')
                return
            try:  # 尝试读取文件
                f = open(fmap[ucode], 'rb')
                fs = os.fstat(f.fileno())
                self.send_response(HTTPStatus.OK)
                self.send_header("Filename", quote(fmap[ucode].split('/')[-1]))
                self.send_header("Size", str(fs[6]))
                self.send_header('Sha256', calcsha256(fmap[ucode]))
                self.end_headers()
            except:
                self.send_error(HTTPStatus.NOT_FOUND, 'File not found.')
                try:
                    f.close()
                except (UnboundLocalError, AttributeError):
                    pass
        elif self.path == '/favicon.ico' or self.path == '' or self.path[0:3] != '/s/':
            # 忽略请求图标等
            self.send_response(200)
            self.end_headers()
            return
        elif self.path.startswith('/s/'):
            # 文件下载(客户端发送)
            code = self.path.split('/')[2]
            ucode = unquote(code)
            if ucode not in fmap:
                self.send_error(HTTPStatus.NOT_FOUND, 'File not Found')
                return
            self.send_response(HTTPStatus.FOUND)  # 重定向的响应码
            s = '/sdown/%s/%s' % (ucode, fmap[ucode].split('/')[-1])  # 重定向地址
            s = quote(s)  # 编码为ASCII
            self.send_header("Location", s)
            self.end_headers()

    def do_POST(self):
        """接收Python对象(json)
"""
        clen = int(self.headers['Content-Length'])  # POST长度
        try:
            body = self.rfile.read(clen)
            res = loads(body)  # 从json转换为Python对象
            resp = receive_func(res)  # 调用用户设定的函数,传入收到的对象
            if resp:
                self.send_response(resp[0])
                self.end_headers()
                self.wfile.write(dumps(resp[1]).encode())
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'')
        except Exception as e:
            print('An exception has occurred while responding a POST request: ', type(
                e), e, file=stderr)


def default_addr(ip: str, port: str):
    """设定send函数默认发送地址，无返回值
格式：default_addr(ip:str, port:str)
"""
    global daddr
    daddr = prot + ip + ':' + str(port)  # 拼接地址


def send(obj: object, ip: str=None, port: int=None, timeout: int=2):
    """发送可以被转换为json字符串的Python对象
格式：send(obj:onject, ip:str, port:int, timeout:int)
obj：要发送的对象
ip：发送到的IP地址
port：发送到的端口
timeout：超时时间，默认为2
ip, port若不填则使用default_addr设定的默认IP地址及端口
"""
    r = None
    try:
        addr = prot + ip + ':' + str(port)
    except Exception:  # 如果有变量为None，则使用默认地址
        addr = daddr
    if addr == None:
        raise InvalidAddress("地址无效")
    s = dumps(obj)  # 转换为json
    try:
        r = urlopen(addr, data=s.encode(), timeout=timeout)  # 发送对象
    except ImportError as e:
        ...
        print(e)
    return r.getcode(), r.read()


def receive(func):
    """装饰器，被装饰函数为收到Python对象时调用，会传入收到的对象
"""
    global receive_func
    receive_func = func
    return func


def downpath(path: str=None):
    """为filedown设定文件下载路径,不传入参数返回当前默认路径
"""
    global defpath
    if path is None:
        return defpath
    defpath = path


def filedown(url: str, file: str=None, report=None):
    """文件下载
格式：filedown(url:str, file:str, report=None)
从指定的URL下载文件，file为文件名
filedown(url:str,report=None)
用于swdlc的文件分享
url='https://<IP>:<port>/s/<sharecode>'
report为回调函数
"""

    def reporthook(blocknum, blocksize, totalsize):
        percent = int(100 * blocknum * blocksize / totalsize)
        if percent > 100:
            percent = 100
        report(percent)

    if file == None:
        t = urlparse(url)
        addr = t.netloc.split(':')
        ip = addr[0]
        port = int(addr[1])
        code = t.path.split('/')[2]  # 获取文件分享代码
        file = getfileinfo(ip, port, code)[0]
    try:
        file = (defpath + '/' + file).replace('//', '/')
    except Exception:
        ...
    '''if os.path.commonprefix((os.path.realpath(file), os.path.realpath(defpath))) != os.path.realpath(defpath):
        print(os.path.commonprefix((os.path.realpath(file), defpath)),
              os.path.realpath(defpath))
        return'''
    HTTPErrorProcessor.https_response = http_response_backup
    HTTPErrorProcessor.http_response = http_response_backup
    f, h = urlretrieve(url, file, reporthook=reporthook if report !=  # @UnusedVariable
                       None else None)
    HTTPErrorProcessor.http_repsonse = HTTPErrorProcessor.https_response = http_response
    file = open(file)
    file.close()


def getfileinfo(ip: str, port: int, code: str):
    code = quote(code)
    url = prot + ip + ':' + str(port) + '/fileinfo/' + code
    t = urlopen(url)
    h = str(t.info()).split('\n')
    fn = ''
    size,sha256 = '',''
    for i in h:
        if i.startswith('Filename'):
            fn = unquote(i.split(':')[1][1:])
        elif i.startswith('Size'):
            size = unquote(i.split(':')[1][1:])
        elif i.startswith('Sha256'):
            sha256 = unquote(i.split(':')[1][1:])
    info = fn, size, sha256
    return info


def share(code: str, filepath: str, times: int=-1):
    """创建分享链接
code：分享代码
filepath：文件名(含路径)
times：允许下载次数(若输入小于零则无限次)
"""
    fmap[code] = filepath
    stimes[code] = times


def rmshare(code):
    """移除分享代码为code的链接(不删除文件)
返回值：
成功：0
找不到分享代码：1
"""
    try:
        del fmap[code]
    except Exception:  # 找不到分享代码
        return 1
    return 0


def init(port: int=0, daemon: bool=True, enable_TLS: bool=True):
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
    prot = 'https://' if enable_TLS else 'http://'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:  # 检测端口占用
        sock.bind(('0.0.0.0', port))  # 若无法绑定则说明端口已被占用
    except OSError:
        return 1
    finally:
        sock.close()
    sock.close()
    port = int(port)
    sport = port
    httpd = ThreadingHTTPServer(('0.0.0.0', port), SHRH)  # 创建服务器
    if enable_TLS:  # 套接字
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)  # 创建上下文
        context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')  # 证书
        httpd.socket = context.wrap_socket(
            httpd.socket, server_side=True)  # 修改套接字
    t = threading.Thread(daemon=daemon, target=httpd.serve_forever)  # 创建线程
    t.start()  # 启动线程
    return 0


if __name__ == '__main__':
    if init(65140, False):
        print('端口已被占用')
        raise SystemExit
    default_addr(getip(), '65140')

    @receive  # 接收函数
    def receive(obj):
        print(obj)
        return 500, 'received'

    sleep(1)
    print(send(5))
