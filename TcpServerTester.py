from socketserver import BaseRequestHandler, ThreadingTCPServer

ENCODING = 'utf-8'
BUFSIZE = 1024
SERVER_IP = '172.24.27.53'
TCP_PORT = 65530

class TcpHandler(BaseRequestHandler):
    def handle(self):
        print('Get connection from', self.client_address)
        self.MsgGetter()

    def MsgGetter(self):
        i = 0
        while True:
            msg = self.request.recv(BUFSIZE).decode(ENCODING)
            if msg:
                print('From {} get message : {} '.format(self.client_address, msg))
                self.request.send(bytes('收到%s'%(str(i)), ENCODING))
                i +=1

class Listener:
    def __init__(self, ip, port):
        self.server = ThreadingTCPServer((ip, port), TcpHandler)
        # self.server = TCPServer((ip, port), TcpHandler)

    def run(self):
        self.server.serve_forever()

if __name__ == '__main__':
    Listener(SERVER_IP,TCP_PORT).run()
