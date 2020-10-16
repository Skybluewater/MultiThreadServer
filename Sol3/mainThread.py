import socket
import threading
import inspect
import ctypes
from threading import Event
import time

numberOfConn = 20
listThread = []
lock = threading.RLock()
clientIDArray = []
event = Event()
clientDetails = []
threadNumber = 0

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


def check_client(newSocket: socket.socket, tid, fatherThread: threading.Thread):
    while True:
        event.wait()
        global threadNumber, listThread
        flag = 0
        lock.acquire()
        try:
            if threadNumber == tid:
                print("find conflict tid: " + str(tid))
                ### 先关闭父进程不再socket 读报错
                stop_thread(fatherThread)
                newSocket.close()
                listThread.remove(tid)
                print("lthread number %s release" %str(tid))
                print("lthread: ", str(listThread))
                clientIDArray[tid] = 0
                flag = 1
                event.clear()
                break
        finally:
            lock.release()
            if flag == 1:
                stop_thread(threading.current_thread())
            print("tid %s starts waiting" % str(tid))
            time.sleep(0.01)


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
    client_deamon = threading.Thread(target=check_client, args=(newSocket, tid, threading.currentThread()))
    client_deamon.start()
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
            finally:
                lock.release()
            newSocket.close()
            stop_thread(client_deamon)
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
        if len(listThread) >= 5:
            lock.acquire()
            threadNumber = listThread[0]
            lock.release()
            print("the pid wrong find: " + str(threadNumber))
            event.set()
            event.wait()
        client = threading.Thread(target=deal_client, args=(client_socket, client_port, clientID))
        client.start()
 
 
if __name__ == '__main__':
    for i in range(0, numberOfConn):
        clientIDArray.append(0)
    main()
