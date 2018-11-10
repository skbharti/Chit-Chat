import getpass 
import socket
import ast
import threading
import json

UNSUCCESSFUL = '[UNSUCCESSFUL]'
PASSWORD = '[PASSWORD]'
TOO = '[TOO]'

users = {'skb':'abc123','ams':'bcd123'}
user_port_map = {}
def server_program():
    # get the hostname
    host = socket.gethostname()
    file = open("port.txt","r") 
    port = int(file.read())+1  # initiate port no above 1024
    print("Port: ",port)
    file.close()

    file = open("port.txt","w") 
    file.write(str(port))  # initiate port no above 1024
    file.close()

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(5)
    threads = []
    while(True):
        print('Waiting for Connections')
        conn, addr = server_socket.accept()  # accept new connection
        # print(conn,address)
        print("Connection from: " + str(addr))

        t = threading.Thread(target=server_thread, args=(conn,addr,))
        threads.append(t)
        t.daemon = True
        t.start()

    for t in threads:
        t.join()

    server_socket.close()

def server_thread(conn,addr):
    while(True):
        data_json = conn.recv(1024).decode()
        token, userdata = parse_json(data_json)
        if(token=='AUTH'):
            response = authenticate(userdata, addr)
            if(response==1):
                data = {'TOKEN': 'SUCCESS', 'SERVERDATA': 'Authentication Successful'}
                data_json = json.dumps(data)
                conn.send(data_json.encode())
            else:
                data = {'TOKEN': 'UNSUCCESS', 'SERVERDATA': 'Authentication Unsuccessful'}
                data_json = json.dumps(data)
                conn.send(data_json.encode())

        elif(token=='SINGLECHAT'):
            # reject if user is not online  # threads are to be created to deal with it
            # accept and send if he is online
            pass

        elif(token=='GROUPCHAT'):
            # reject if no user in the group is online
            # accept and send to the group users online
            pass

        elif(token=='END'):
            break
        
    
def authenticate(data,addr):
    userid = data['USERID']
    password = data['PASSWORD']
    user_port_map[userid] = addr[1]
    if(userid in users.keys()):
        if(password == users[userid]):
            return 1
    return 0


def parse_json(data_json):
    data = ast.literal_eval(data_json)
    print(data,type(data))
    return data['TOKEN'], data['USERDATA']


if __name__ == '__main__':
    server_program()
