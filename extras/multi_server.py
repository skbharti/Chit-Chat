import getpass 
import socket
from _thread import *
import threading 

print_lock = threading.Lock() 

UNSUCCESSFUL = '[UNSUCCESSFUL]'
PASSWORD = '[PASSWORD]'
TOO = '[TOO]'

users = {'skb':'abc123','ams':'bcd123'}
user_port_map = {}
port_user_map = {}

def server_program():
	# get the hostname
	host = socket.gethostname()
	port = 5111  # initiate port no above 1024

	server_socket = socket.socket()  # get instance
	# look closely. The bind() function takes tuple as argument
	server_socket.bind((host, port))  # bind host address and port together

	# configure how many client the server can listen simultaneously
	server_socket.listen(5)
	threads = []
	while(True):
		print('Waiting for Connections Here')
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
	print('This is a Server Thread')
	response = authenticate(conn,addr)

	if(response==1):
		data = 'Authentication Successful!'
		conn.send(data.encode())
	elif(response==2):
		data = TOO+' much invalid attempts!'
		conn.send(data.encode())
		conn.close()
		return
	else:
		data = 'Authentication '+UNSUCCESSFUL
		conn.send(data.encode())
		conn.close()
		return

	while True:
		# receive data stream. it won't accept data packet greater than 1024 bytes
		data = conn.recv(1024).decode()
		if not data:
			# if data is not received break
			break
		print("from connected user "+port_user_map[addr[1]]+" : " + str(data))
		data = input(' -> ')
		conn.send(data.encode())  # send data to the client

	conn.close()  # close the connection

def authenticate(conn,addr):
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
			user_port_map[user_id] = addr[1]
			port_user_map[addr[1]] = user_id 
			print(user_port_map)
			return 1

	return 0

if __name__ == '__main__':
	server_program()
