import getpass 
import socket
import json
import ast
import threading
from time import sleep

from tkinter import *


lock = threading.Lock()

UNSUCCESSFUL = '[UNSUCCESSFUL]'
PASSWORD = '[PASSWORD]'
TOO = '[TOO]'
USERID = ''

def client_program():
	host = socket.gethostname()  # as both code is running on same pc
	file = open("port.txt","r") 
	port = int(file.read())  # initiate port no above 1024
	print("Port: ",port)
	file.close()
	
	client_socket = socket.socket()  # instantiate
	client_socket.connect((host, port))  # connect to the server

	l = authenticate(client_socket)
	response = l[0]
	USERID = l[1]
	
	count = 0
	while(response==0):
		print("Authentication Unsuccessful, Retry!")
		count+=1
		if(count>5):
			print("Too many attempts!")
			exit(0)
			l = authenticate(client_socket)
			response = l[0]
			USERID = l[1]

	print('Authentication Successful Here!')

	file = "./"+USERID+".txt"

	option = input('========================================================================\n\t\t[1.] Individual Chat [2.] Group Chat [3.] Exit\t\t\n========================================================================\n-> ')
	if(option == '1'):
		t = threading.Thread(target=recv_msg, args=(client_socket,file,USERID,))

		tgui = threading.Thread(target=gui, args=())
		tgui.daemon = True
		tgui.start()
		t.daemon = True
		t.start()
		while(True):
			connecting_user = input('User ID: ')
			message = input('-> ')
			data = {'TOKEN':'SINGLECHAT', 'USERDATA':{'RECV_ID': connecting_user, 'TEXT':message}}
			f = open(file, "a")
			f.write(USERID+"->"+connecting_user+": "+message+"\n")
			f.close()
			data_json = json.dumps(data)
			client_socket.send(data_json.encode())
			sleep(0.1)

				
	if(option == 2):
		pass
		# implement group chat here
	if(option == 3):
		data = {'TOKEN': 'END', 'USERDATA':''}
		data_json = json.dumps(data)
		
		client_socket.send(data_json.encode())
		client_socket.close()  # close the connection
	
def gui():
	root = Tk()
	S = Scrollbar(root)
	T = Text(root, height=30, width=50)
	S.pack(side=RIGHT, fill=Y)
	T.pack(side=LEFT, fill=Y)
	S.config(command=T.yview)
	T.config(yscrollcommand=S.set)
	with open(USERID+".txt") as file:
		data = file.read()
	T.insert(END, data)
	mainloop()


def recv_msg(client_socket):
	while(True):
		data_json = client_socket.recv(1024).decode()
		token, userdata = parse_json(data_json)
		lock.acquire()
		print(userdata)
		lock.release()


def recv_msg(client_socket,file,user):
	while(True):
		data_json = client_socket.recv(1024).decode()
		token, serverdata = parse_json(data_json)
		f = open(file, "a")
		f.write(serverdata['SEND_ID']+"->"+user+": "+serverdata['TEXT']+"\n")
		f.close()
		lock.acquire()
		print(serverdata)
		lock.release()


def authenticate(client_socket):
	userid = input("Enter your userid: ")
	password = getpass.getpass("Enter your password: ")
	data = {'TOKEN': 'AUTH', 'USERDATA': {'USERID': userid, 'PASSWORD': password}}
	data_json = json.dumps(data)
	client_socket.send(data_json.encode())
	
	data_json = client_socket.recv(1024).decode()
	
	token, serverdata = parse_json(data_json)
	if(token=='SUCCESS'):
		return [1,userid]
	else:
		return [0,userid]

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
	# print(data,type(data))
	return data['TOKEN'], data['SERVERDATA']


if __name__ == '__main__':
	client_program()
