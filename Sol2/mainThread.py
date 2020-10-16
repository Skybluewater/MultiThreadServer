import socket
import threading
import inspect
import ctypes
from threading import Event
import clientServer as cS

numberOfConn = 20

def findInArray() -> int:
    for i in range(numberOfConn):
        if cS.clientIDArray[i] == 0:
            return i


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", 7788))
    server.listen(128)

    print("server is running!")
    while True:
        client_socket, client_port = server.accept()
        print("client [%s] is connected!" % str(client_port))
        clientID = findInArray()
        cS.clientIDArray[clientID] = 1
        cS.listThread.append(clientID)
        print("length of list start: " + str(cS.listThread))
        if len(cS.listThread) > 2:
            cS.lock.acquire()
            cS.threadNumber = cS.listThread[0]
            print("listThread in main: " + str(id(cS.listThread)))
            print("clientIDArrad in main: " + str(id(cS.clientIDArray)))
            cS.lock.release()
            print("the pid wrong find: " + str(id(cS.threadNumber)))
            print("the server Event's id is: " + str(id(cS.serverEvent)))
            cS.event.set()
            cS.serverEvent.wait()
            cS.serverEvent.clear()
        client = threading.Thread(target=cS.deal_client, args=(client_socket, client_port, clientID))
        client.start()
 
 
if __name__ == '__main__':
    for i in range(0, numberOfConn):
        cS.clientIDArray.append(0)
    main()
