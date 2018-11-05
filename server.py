import getpass 
import socket

UNSUCCESSFUL = '[UNSUCCESSFUL]'
PASSWORD = '[PASSWORD]'
TOO = '[TOO]'

users = {'skb':'abc123','ams':'bcd123'}
def server_program():
    # get the hostname
    host = socket.gethostname()
    port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(5)
    while(True):
        print('Waiting for Connections')
        conn, address = server_socket.accept()  # accept new connection
        # print(conn,address)
        print("Connection from: " + str(address))

        response = authenticate(conn)

        if(response==1):
            data = 'Authentication Successful!'
            conn.send(data.encode())
        elif(response==2):
            data = TOO+' much invalid attempts!'
            conn.send(data.encode())
            conn.close()
            continue
        else:
            data = 'Authentication '+UNSUCCESSFUL
            conn.send(data.encode())
            conn.close()
            continue

        while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()
            if not data:
                # if data is not received break
                break
            print("from connected user: " + str(data))
            data = input(' -> ')
            conn.send(data.encode())  # send data to the client

        conn.close()  # close the connection


def authenticate(conn):
    send_data = 'Please enter your userid'
    conn.send(send_data.encode())

    user_id = conn.recv(1024).decode()
    
    count = 1
    while(user_id not in users.keys() and count<=2):
        send_data = 'Invalid User! Retry! Please enter your userid'
        conn.send(send_data.encode())
        count+=1
        user_id = conn.recv(1024).decode()

    if(count>2):
        return 2


    send_data = 'Please enter your '+PASSWORD
    conn.send(send_data.encode())

    password = conn.recv(1024).decode()
    if not password:
        # if data is not received break
        pass

    if(user_id in users.keys()):
        if(password == users[user_id]):
            return 1

    return 0

if __name__ == '__main__':
    server_program()
