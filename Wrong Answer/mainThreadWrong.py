import socket
import threading
import inspect
import ctypes
from threading import Event
from clientServer import deal_client, listThread, threadNumber, clientIDArray, event, lock
import clientServer as cS

numberOfConn = 20


def findInArray() -> int:
    for i in range(numberOfConn):
        if clientIDArray[i] == 0:
            return i


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", 7788))
    server.listen(128)
    global listThread, clientIDArray, threadNumber
    print("server is running!")
    while True:
        client_socket, client_port = server.accept()
        print("client [%s] is connected!" % str(client_port))
        clientID = findInArray()
        clientIDArray[clientID] = 1
        listThread.append(clientID)
        print("length of list start: " + str(listThread))
        if len(listThread) > 2:
            lock.acquire()
            threadNumber = listThread[0]
            print("listThread in main: " + str(id(listThread)))
            print("clientIDArrad in main: " + str(id(clientIDArray)))
            ''' '''
            lock.release()
            print("the pid wrong find: " + str(id(threadNumber)))
            event.set()
            event.wait()
        client = threading.Thread(target=deal_client, args=(client_socket, client_port, clientID))
        client.start()
 
 
if __name__ == '__main__':
    for i in range(0, numberOfConn):
        clientIDArray.append(0)
    main()
