import getpass 
import socket
import json
import ast


UNSUCCESSFUL = '[UNSUCCESSFUL]'
PASSWORD = '[PASSWORD]'
TOO = '[TOO]'

def client_program():
	host = socket.gethostname()  # as both code is running on same pc
	file = open("port.txt","r") 
	port = int(file.read())  # initiate port no above 1024
	print("Port: ",port)
	file.close()
	
	client_socket = socket.socket()  # instantiate
	client_socket.connect((host, port))  # connect to the server

	response = authenticate(client_socket)
	
	count = 0
	while(response==0):
		print("Authentication Unsuccessful, Retry!")
		count+=1
		if(count>5):
			print("Too many attempts!")
			exit(0)
		response = authenticate(client_socket)

	print('Authentication Successful Here!')
	option = input('========================================================================\n\t\t[1.] Individual Chat [2.] Group Chat [3.] Exit\t\t\n========================================================================\n-> ')
	if(option == 1):
		connecting_user = input('User ID: ')
		message = input('-> ')
		data = {'TOKEN':'SINGLECHAT', 'USERDATA':{'RECV_ID': connecting_user, 'TEXT':message}}
		data_json = json.dumps(data)
		client_socket.send(data_json.encode())

	elif(option == 2):
		pass
		# implement group chat here
	elif(option == 3):
		data = {'TOKEN': 'END', 'USERDATA':''}
		data_json = json.dumps(data)
		client_socket.send(data_json.encode())
		client_socket.close()  # close the connection
	

	

def authenticate(client_socket):
	userid = input("Enter your userid: ")
	password = getpass.getpass("Enter your password: ")
	data = {'TOKEN': 'AUTH', 'USERDATA': {'USERID': userid, 'PASSWORD': password}}
	data_json = json.dumps(data)
	client_socket.send(data_json.encode())
	
	data_json = client_socket.recv(1024).decode()
	
	token, serverdata = parse_json(data_json)
	if(token=='SUCCESS'):
		return 1
	else:
		return 0

def handle_chat(client_socket):
	while(True):
		message = input('-> ')
		data_json = {'TOKEN': 'DIRECTCHAT', 'USERDATA': message}
		data_json = json.dumps(data)
		client_socket.send(data_json.encode())

		data_json = client_socket.recv(1024).decode()
		token, userdata = parse_json(data_json)
		if(token == 'DIRECTCHAT'):
			print(userdata)

def parse_json(data_json):
    data = ast.literal_eval(data_json)
    print(data,type(data))
    return data['TOKEN'], data['SERVERDATA']


if __name__ == '__main__':
	client_program()
