import socket
import threading
import inspect
import ctypes
import sqlite3


listThread = []
lock = threading.RLock()
clientIDArray = []
clientEvent = []
threadNumber = 0
serverEvent = threading.Event()


DOCUMENTS_ROOT = "./web"


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


def check_client(newSocket: socket.socket, tid, fatherThread: threading.Thread, event):
    event.wait()
    lock.acquire()
    try:
        stop_thread(fatherThread)
        newSocket.close()
        clientIDArray[tid] = 0
        # pop
        clientEvent.pop(listThread.index(tid))
        listThread.remove(tid)
        # print
        print("lthread number %s release" %str(tid))
        print("lthread: ", str(listThread))
    finally:
        lock.release()
        serverEvent.set()
    stop_thread(threading.current_thread())


def deal_login(data: list, client_socket: socket.socket):
    username = data[-1].split("&")[0]
    password = data[-1].split("&")[1]
    username = username[9:]
    password = password[9:]
    lock.acquire()
    try:
        conn = sqlite3.connect("computerNetwork.db")
        cursor = conn.cursor()
        instructQuery = """
            select * from UserData where username == "{user}"
        """.format(user = username)
        cursor.execute(instructQuery)
        queryResult = cursor.fetchall()
        if cursor.rowcount == 0:
            cursor.close()
        else:
            ifFind = 0
            for i in queryResult:
                if i[1] == password:
                    ifFind = 1
                    cursor.close()
                    conn.close()
                    wrap(client_socket, statusCode = 200)
                    break
            if ifFind == 0:
                cursor.close()
                conn.close()
                wrap(client_socket, statusCode = 404)
    finally:
        lock.release()



def wrap(client_socket, statusCode = 200, path = ""):
    if statusCode == 200:
        if path == "":
            location = DOCUMENTS_ROOT + '/index.html'
        else:
            location = DOCUMENTS_ROOT + path
        if "css" in location:
            print("*****************find css****************")
            try:
                f = open(location, 'rb')
                reply_body = f.read()
                f.close()
                reply_head = 'HTTP/1.1 200 OK \r\n'
                reply_head += '\r\n'
            finally:
                client_socket.send(reply_head.encode('utf-8'))
                client_socket.send(reply_body)
        elif ".html" in location:
            try:
                f = open(location, 'rb')
            except IOError:
                reply_head = 'HTTP/1.1 404 not found\r\n'
                reply_head += '\r\n'
                f = open("./web/notFound.html", 'rb')
                reply_body = f.read()
                f.close()
            else:
                reply_head = 'HTTP/1.1 200 OK \r\n'
                reply_head += '\r\n'
                reply_body = f.read()
                f.close()
            finally:
                client_socket.send(reply_head.encode('utf-8'))
                client_socket.send(reply_body)
                '''
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
            client_socket.send(reply_body)'''
    elif statusCode == 404:
        reply_head = 'HTTP/1.1 404 not found\r\n'
        reply_head += '\r\n'
        f = open("./web/notFound.html", 'rb')
        reply_body = f.read()
        f.close()
        client_socket.send(reply_head.encode('utf-8'))
        # 再返回body
        client_socket.send(reply_body)


def deal_client(newSocket: socket.socket, addr, tid, event):
    client_deamon = threading.Thread(target=check_client, args=(newSocket, tid, threading.currentThread(), event))
    client_deamon.start()
    while True:
        data = newSocket.recv(1024).decode('utf-8', errors='ignore')
        if data:
            data_info = data.splitlines()
            for i in data_info:
                print(i)
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
            elif target_method == "POST":
                if target_file == "/login.html":
                    deal_login(data_info, newSocket)
        else:
            print("client [%s] exit" % str(addr))
            lock.acquire()
            try:
                clientEvent.pop(listThread.index(tid))
                listThread.remove(tid)
                clientIDArray[tid] = 0
            finally:
                lock.release()
            newSocket.close()
            stop_thread(client_deamon)
            break
