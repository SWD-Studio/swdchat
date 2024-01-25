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
#    You can contact us on swd-go.yespan.com.
from http.server import HTTPServer as HS,SimpleHTTPRequestHandler as SHRH
from http.server import BaseHTTPRequestHandler as BHRH
import ssl
import socket
myip=socket.gethostbyname(socket.gethostname())
def getip():
    return myip
def serve(directory,port):
    class Ft(SHRH):
        def __init__(self, *args, **kwargs):
            self.directory = directory
            BHRH.__init__(self,*args, **kwargs)
    h=HS((getip(),port),Ft)
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
    h.socket=context.wrap_socket(h.socket,server_side=True)
    h.serve_forever()
if __name__=='__main__':
    serve('.',44300)
