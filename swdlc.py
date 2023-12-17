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
#20231210
#类型注释
#添加函数downpath(path=None),用于指定默认下载目录,path为None则返回默认目录
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
daddr=None
ssl._create_default_https_context=ssl._create_unverified_context
myip=socket.gethostbyname(socket.gethostname())
def getip():
    return myip
class InvalidAddress(Exception):pass
def prerr(s:str):
    print(s,file=stderr)
fmap={}#code:fpath
class SHRH(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path[0:7]=='/sdown/':
            code=self.path.split('/')[2]
            ucode=unquote(code)
            if ucode not in fmap:
                self.send_error(HTTPStatus.NOT_FOUND,'Code not found.')
                return
            try:
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
                except UnboundLocalError:
                    pass
            if f:
                try:
                    shutil.copyfileobj(f,self.wfile)
                finally:
                    f.close()
        elif self.path[0:9]=='/getname/':
            code=self.path.split('/')[2]
            ucode=unquote(code)
            if ucode not in fmap:
                self.send_error(HTTPStatus.NOT_FOUND,'Code not found.')
                return
            self.send_response(200)
            self.send_header(quote(fmap[ucode].split('/')[-1]), '')
            self.end_headers()
        elif self.path=='/favicon.ico' or self.path=='' or self.path[0:3]!='/s/':
            self.send_response(200)
            self.end_headers()
            return
        elif self.path[0:3]=='/s/':
            code=self.path[3:]
            ucode=unquote(code)
            if ucode not in fmap:
                self.send_error(HTTPStatus.NOT_FOUND,'File not Found')
                return
            self.send_response(HTTPStatus.FOUND)
            s='/sdown/%s/%s'%(ucode,fmap[ucode].split('/')[-1])
            s=quote(s)
            self.send_header("Location", s)
            self.end_headers()
    def do_POST(self):
        clen=int(self.headers['Content-Length'])
        try:
            body=self.rfile.read(clen)
            res=loads(body)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'200 OK')
            receive_func(res)
        except Exception as e:
            print(e)
def default_addr(ip:str,port:str):
    global daddr
    daddr='https://'+ip+':'+str(port)
def send(obj:object,ip:str=None,port:str=None):
    try:
        addr='https://'+ip+':'+str(port)
    except Exception:
        addr=daddr
    if addr==None:
        raise InvalidAddress
    s=dumps(obj)
    try:
        urlopen(addr,data=s.encode(),timeout=2)
    except BadStatusLine as e:
        ...
        #print(e)
def receive(func):#@
    global receive_func
    receive_func=func
    return func
def downpath(path:str=None):
    global defpath
    if path is None:
        return defpath
    defpath=path
def filedown(url:str,file:str=None,report=None):
    def reporthook(blocknum,blocksize,totalsize):
        percent=int(100*blocknum*blocksize/totalsize)
        if percent>100:
            percent=100
        report(percent)  
    if file==None:
        t=urlopen(url.replace('/s/','/getname/'))
        file=unquote(str(t.headers).split('\n')[2][:-2])
        #print(str(t.headers).split('\n')[-1],t.headers,sep='\n')
    try:
        file=(defpath+'/'+file).replace('//','/')
    except Exception:
        ...
    f,h=urlretrieve(url,file,reporthook=reporthook if report!=None else None)
def share(code:str,filepath:str):
    fmap[code]=filepath
def rmshare(code):
    try:
        del fmap[code]
    except Exception:
        return 1
    return 0
def init(port:int=36144,daemon:bool=True):
    global httpd
    global sport
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.settimeout(1)
    if not sock.connect_ex((getip(),port)):
        return 1
    port=int(port)
    sport=port
    httpd=ThreadingHTTPServer((getip(),port),SHRH)
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
    httpd.socket=context.wrap_socket(httpd.socket,server_side=True)
    t=threading.Thread(daemon=daemon,target=httpd.serve_forever)
    t.start()
    return 0
if __name__=='__main__':
    if init(65140,False):
        print('端口已被占用')
        raise SystemExit
    default_addr(getip(),'65140')
    @receive
    def receive(obj):
        print(obj)
    send(5)
