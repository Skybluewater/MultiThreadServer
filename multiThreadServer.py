import socket
from threading import Thread
from clientHandler import client_server


DOCUMENTS_ROOT = './html'
SERVER_ADDR = (ADDR, PORT) = ("", 7788)
 
 
class WebServer():
 
    def __init__(self, addr):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(addr)
        self.server.listen(128)

    def run_last(self):
        while True:
            clinet_socket, client_port = self.server.accept()
            # 显示连接
            print('address:' + str(client_port) + ' connected')
            t = Thread(target=self.client(clinet_socket))
            t.start()
            clinet_socket.close()


    def client(self, client_socket):
        client_server(client_socket)
 
 
def main():
    http_server = WebServer(SERVER_ADDR)
    print("Server is start on port:" + str(PORT))
    http_server.run_last()
 
 
if __name__ == '__main__':
    main()
