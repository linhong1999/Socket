from socketserver import BaseRequestHandler, ThreadingUDPServer

ENCODING = 'utf-8'
BUFSIZE = 1024
SERVER_IP = '127.0.0.1'
# SERVER_IP = '192.168.244.1' #虚拟机网关
UDP_PORT = 65531
class UdpHandler(BaseRequestHandler):
    def handle(self):
        print('Get connection from', self.client_address)
        self.MsgGetter()

    def MsgGetter(self):

        msg,sock = self.request
        if msg:
            print('From {} get message : {} '.format(self.client_address, msg.decode(ENCODING)))
            msg, sock = self.request
            sock.sendto(msg,self.client_address)

class Listener:
    def __init__(self, ip, port):
        self.server = ThreadingUDPServer((ip, port), UdpHandler)

    def run(self):
        self.server.serve_forever()

if __name__ == '__main__':
    Listener(SERVER_IP,UDP_PORT).run()