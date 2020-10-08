import socket
import re
import requests
import sqlite3

DOCUMENTS_ROOT = "./html"


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
            client_socket.close()
    elif statusCode == 404:
        reply_head = 'HTTP/1.1 404 not found\r\n'
        reply_head += '\r\n'
        reply_body = b'not found'
        client_socket.send(reply_head.encode('utf-8'))
        # 再返回body
        client_socket.send(reply_body)
        client_socket.close()


def client_server(client_socket):
    recv_data = client_socket.recv(1024).decode('utf-8', errors='ignore')
    data_info = recv_data.splitlines()
    # for i in data_info:
    #     print(i)
    # 获取输入的信息（地址）
    target = data_info[0]
    target_file = target.split()[1]
    target_request_type = target.split()[0]
    print("file name is " + target_file)
    print("target request type is " + target_request_type)
    if target_request_type == "POST":
        if target_file == "/login":
            username = data_info[-1].split("&")[0]
            password = data_info[-1].split("&")[1]
            username = username[9:]
            password = password[9:]
            conn = sqlite3.connect("computerNetwork.db")
            cursor = conn.cursor()
            instructQuery = """
                select * from UserData where username == "{user}"
            """.format(user = username)
            print(instructQuery)
            cursor.execute(instructQuery)
            queryResult = cursor.fetchall()
            if len(queryResult) == 0:
                cursor.close()
                conn.close()
                wrap(client_socket, statusCode=404)
            else:
                ifFind = 0
                for i in queryResult:
                    if i[1] == password:
                        ifFind = 1
                        cursor.close()
                        conn.close()
                        wrap(client_socket, statusCode=200)
                        break
                if ifFind == 0:
                    cursor.close()
                    conn.close()
                    wrap(client_socket, statusCode=404)
    elif target_request_type == "GET":
        if target_file == '/':
            wrap(client_socket, 200)
        else:
            wrap(client_socket, 200, path=target_file)
