from socketserver import BaseRequestHandler, ThreadingUDPServer

ENCODING = 'utf-8'
BUFSIZE = 1024
SERVER_IP = '192.168.244.1'
# SERVER_IP = '192.168.244.1' #虚拟机网关
UDP_PORT = 65531
ROUTE_MAP = {
    'self': '192.168.244.1',
    'she': '192.168.244.129',
}
CONN_MAP = {
    '192.168.244.1':{
        'port':None,'sock':None,
    },
    '192.168.244.129':{
        'port':None,'sock':None,
    },
}

class UdpHandler(BaseRequestHandler):
    def handle(self):
        print('Get connection from', self.client_address)
        self.MsgGetter()

    def MsgGetter(self):
        # while True:
        # try:
        msg,sock = self.request
        if msg:
            print('From {} get message : {} '.format(self.client_address, msg))
            ip,port = self.client_address
            #每次更新套接字和端口
            CONN_MAP[ip]['port'] , CONN_MAP[ip]['sock']= port,sock
            msg = str(msg,encoding=ENCODING)
            self.MsgSender(msg.split()[0],msg.split()[1])

    def MsgSender(self, obj,str):
        try:
            msg, sock = self.request
            if msg:
                CONN_MAP[ROUTE_MAP[obj]]['sock'].sendto(msg,(ROUTE_MAP[obj], CONN_MAP[ROUTE_MAP[obj]]['port']))
                # CONN_LIST[ROUTE_MAP[str]]['sock'].sendto(msg, CONN_LIST[ROUTE_MAP[str]]['client_address'])
        except:
            print('Close an connection from {}'.format((ROUTE_MAP[obj],CONN_MAP[ROUTE_MAP[obj]]['port'])))

class Listener:
    def __init__(self, ip, port):
        self.server = ThreadingUDPServer((ip, port), UdpHandler)

    def run(self):
        self.server.serve_forever()

if __name__ == '__main__':
    Listener(SERVER_IP,UDP_PORT).run()