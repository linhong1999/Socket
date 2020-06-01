from socketserver import BaseRequestHandler, ThreadingTCPServer
ENCODING = 'utf-8'
BUFSIZE = 1024
SERVER_IP = '127.0.0.1'
TCP_PORT = 65530
ROUTE_MAP = {
    'self': 0,
    'she': 1
}
CONN_LIST = []

class TcpHandler(BaseRequestHandler):
    def handle(self):
        print('Get connection from', self.client_address)
        CONN_LIST.append(self)
        self.MsgGetter()

    def MsgGetter(self):
        while True:
            try:
                msg = self.request.recv(BUFSIZE).decode(ENCODING)
                if msg:
                    print('From {} get message : {} '.format(self.client_address, msg))
                    self.MsgSender(msg)
            except:
                print('An unexpected exception appeared when Getter.')

    def MsgSender(self, str):
        try:
            if str == 'she' and len(CONN_LIST) == 1:
                msg = bytes("对方未上线", ENCODING)
                self.request.send(msg)
            else:
                self.request.send(bytes('你选择了%s' % (str), ENCODING))
                try:
                    while True:
                        msg = self.request.recv(BUFSIZE).decode(ENCODING)
                        if msg:
                            msg = bytes(msg, ENCODING)
                          #  self.request.send(bytes('收到了%s' % (str), ENCODING))
                            CONN_LIST[ROUTE_MAP[str]].request.send(msg)
                except:
                    print('Close an connection from {}'.format(CONN_LIST[ROUTE_MAP[str]].client_address))
                    # return True
        except:
            print('An unexpected exception appeared when Sender.')

class Listener:
    def __init__(self, ip, port):
        self.server = ThreadingTCPServer((ip, port), TcpHandler)
        # self.server = TCPServer((ip, port), TcpHandler)
    def run(self):
        self.server.serve_forever()

if __name__ == '__main__':
    Listener(SERVER_IP,TCP_PORT).run()
