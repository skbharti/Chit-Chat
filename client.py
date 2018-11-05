import getpass 
import socket

UNSUCCESSFUL = '[UNSUCCESSFUL]'
PASSWORD = '[PASSWORD]'
TOO = '[TOO]'

def client_program():
	host = socket.gethostname()  # as both code is running on same pc
	port = 5111  # socket server port number

	client_socket = socket.socket()  # instantiate
	client_socket.connect((host, port))  # connect to the server

	response = authenticate(client_socket)

	if(response == 1):
		while data.lower().strip() != 'exit':
			pass
	else:
		client_socket.close()  # close the connection

def authenticate(client_socket):
	while(True):
		data = client_socket.recv(1024).decode() # take input
		print('Received from server: ' + data)  # show in terminal

		if(PASSWORD in data):
			reply = getpass.getpass()
		elif(UNSUCCESSFUL in data or TOO in data):
			return 0
		else:
			reply = input(" -> ")  # again take input
		
		client_socket.send(reply.encode())  # send message

if __name__ == '__main__':
	client_program()
