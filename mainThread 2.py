import socket
import threading
import inspect
import ctypes
from threading import Event


numberOfConn = 20
listThread = []
threadNumber = 0
lock = threading.RLock()
clientIDArray = []
event = Event()
clientDetails = []

thD = []
DOCUMENTS_ROOT = "./html"


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread: threading.Thread):
    _async_raise(thread.ident, SystemExit)


def wrap(client_socket, statusCode = 200, path = ""):
    if statusCode == 200:
        if path == "":
            location = DOCUMENTS_ROOT + '/index.html'
        else:
            location = DOCUMENTS_ROOT + path
        try:
            f = open(location, 'rb')
        except IOError:
            reply_head = 'HTTP/1.1 404 not found\r\n'
            reply_head += '\r\n'
            reply_body = b'not found'
        else:
            reply_head = 'HTTP/1.1 200 OK \r\n'
            reply_head += '\r\n'
            reply_body = f.read()
            f.close()
        finally:
            # 先返回head
            client_socket.send(reply_head.encode('utf-8'))
            # 再返回body
            client_socket.send(reply_body)
    elif statusCode == 404:
        reply_head = 'HTTP/1.1 404 not found\r\n'
        reply_head += '\r\n'
        reply_body = b'not found'
        client_socket.send(reply_head.encode('utf-8'))
        # 再返回body
        client_socket.send(reply_body)


def deal_client(newSocket: socket.socket, addr, tid):
    while True:
        data = newSocket.recv(1024).decode('utf-8', errors='ignore')
        if data:
            data_info = data.splitlines()
            target = data_info[0].split()
            target_method = target[0]
            target_file = target[1]
            print("tid = " + str(tid))
            print(target_file)
            print(target_method)
            print("******************")
            if target_method == "GET":
                if target_file == "/":
                    wrap(newSocket, 200)
                else:
                    wrap(newSocket, 200, path=target_file)
        else:
            print("client [%s] exit" % str(addr))
            lock.acquire()
            try:
                listThread.remove(tid)
                clientIDArray[tid] = 0
                for i in range(len(thD)):
                    if thD[i][0] == tid:
                        thD.pop(i)
                        break
            finally:
                lock.release()
            newSocket.close()
            break


def findInArray() -> int:
    for i in range(numberOfConn):
        if clientIDArray[i] == 0:
            return i


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", 7788))
    server.listen(128)
    global threadNumber
    global listThread, clientIDArray
    print("server is running!")
    while True:
        client_socket, client_port = server.accept()
        print("client [%s] is connected!" % str(client_port))
        clientID = findInArray()
        clientIDArray[clientID] = 1
        listThread.append(clientID)
        print("length of list start: " + str(listThread))
        if len(listThread) > numberOfConn:
            lock.acquire()
            threadNumber = listThread[0]
            print("the pid wrong find: " + str(threadNumber))
            for i in range(len(thD)-1):
                if thD[i][0] == threadNumber:
                    stop_thread(thD[i][2])
                    thD[i][1].close()
                    listThread.remove(threadNumber)
                    clientIDArray[threadNumber] = 0
                    thD.pop(i)
                    break
            lock.release()
        client = threading.Thread(target=deal_client, args=(client_socket, client_port, clientID))
        thD.append((clientID, client_socket, client))
        client.start()
 
 
if __name__ == '__main__':
    for i in range(0, numberOfConn):
        clientIDArray.append(0)
    main()
