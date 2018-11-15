import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import getpass 
import socket
import json
import ast
import threading
import json

UNSUCCESSFUL = '[UNSUCCESSFUL]'
PASSWORD = '[PASSWORD]'
TOO = '[TOO]'

user_port_map = {}
user_conn_map = {}
friends = {}
user_publickey = {}

serverfile = './serverfile.txt'
f = open(serverfile,'a')
f.close()


class Handler:
	server_socket = socket.socket()
	def start_server(self,button):
		host = socket.gethostname()
		file = open("port.txt","r") 
		port = int(file.read())+1
		print("Port: ",port)
		file.close()

		file = open("port.txt","w") 
		file.write(str(port))
		file.close()

		
		self.server_socket.bind((host, port))
		self.server_socket.listen(5)
		self.display(button,"Server Started")

		ta = threading.Thread(target=self.accept, args=())
		ta.daemon = True
		ta.start()

		
	def accept(self):
		threads = []
		while(True):
			print('Waiting for Connections')
			conn, addr = self.server_socket.accept()
			print("Connection from: " + str(addr))
			t = threading.Thread(target=self.client, args=(conn,addr,))
			threads.append(t)
			t.daemon = True
			t.start()
		for t in threads:
			t.join()

	def stop_server(self):
		self.server_socket.close()
		Gtk.main_quit()

	def display(self, button, input_text):
		output_text_buffer = builder.get_object('server_main_display_textbox').get_buffer()
		output_text = output_text_buffer.get_text(output_text_buffer.get_start_iter(), output_text_buffer.get_end_iter(), True) 
		output_text_buffer.set_text(output_text+'\n'+input_text)


	def quit_window(self):
		# this gets executed when 'Quit' button in File Menu is pressed. 
		print("Killing GUI")
		Gtk.main_quit()

	def authenticate(self,data,addr,conn):
		userid = data['USERID']
		password = data['PASSWORD']
		user_port_map[userid] = addr[1]
		user_conn_map[userid] = conn
		f = open(serverfile, 'r')
		# print("opened")
		# print(userid)
		# print(password)
		for line in f:
			value = line.split(',')
			# print(value[0], value[1])
			if(value[0]==userid):
				if(password==value[1][:-1]):
					f.close()
					return 1			

		return 0	

	def client(self,conn,addr):
		while(True):
			data_json = conn.recv(1024).decode()
			token, userdata = self.parse_json(data_json)
			if(token=='AUTH'):
				userid = userdata['USERID']
				response = self.authenticate(userdata, addr, conn)
				if(response==1):
					data = {'TOKEN': 'SUCCESS', 'SERVERDATA':{'TEXT': 'Authentication Successful'}}
					data_json = json.dumps(data)
					conn.send(data_json.encode())
				else:
					data = {'TOKEN': 'UNSUCCESS', 'SERVERDATA':{'TEXT': 'Authentication Unsuccessful'}}
					data_json = json.dumps(data)
					conn.send(data_json.encode())

			elif(token=='SIGNUP'):
				print("recv")
				flag = 0
				userid = userdata['USERID']
				password = userdata['PASSWORD']
				publickey_str = userdata['PUB_KEY']
				f = open(serverfile, 'r')
				for line in f:
					value = line.split(',')
					if(value[0]==userid):
						flag = 1
						break
				f.close()
				if(flag==1):
					data = {'TOKEN': 'UNSUCCESS', 'SERVERDATA':{'TEXT': 'Signup Unsuccessful, username already exists.'}}
					data_json = json.dumps(data)
					conn.send(data_json.encode())
				else:
					f = open(serverfile, 'a')
					f.write(userid+','+password+"\n")
					f.close()
					user_publickey[userid] = publickey_str.encode('utf8')
					data = {'TOKEN': 'SUCCESS', 'SERVERDATA':{'TEXT': 'Signup Successful.'}}
					data_json = json.dumps(data)
					conn.send(data_json.encode())
					friends[userid] = []

			elif(token=='SINGLECHAT'):
				if(userdata['RECV_ID'] not in user_conn_map.keys()):
					data = {'TOKEN':'SINGLECHAT', 'SERVERDATA':{'SEND_ID': 'SERVER', 'TEXT':'The user you are looking for is not online.'}}
					data_json = json.dumps(data)
					conn.send(data_json.encode())
				else:
					conn_rec = user_conn_map[userdata['RECV_ID']]
					data = {'TOKEN':'SINGLECHAT', 'SERVERDATA':{'SEND_ID': userid, 'TEXT':userdata['TEXT']}}
					data_json = json.dumps(data)
					conn_rec.send(data_json.encode())	
				pass
			
			elif(token=='GROUPCHAT'):
				pass

			elif(token=='ADD'):
				if(userdata['USERID'] not in user_conn_map.keys()):
					data = {'TOKEN':'ADDF', 'SERVERDATA': {'TEXT': 'The user you are looking for is not online.'}}
					data_json = json.dumps(data)
					conn.send(data_json.encode())
				else:
					conn_rec = user_conn_map[userdata['USERID']]
					data = {'TOKEN': 'POPUP', 'SERVERDATA': userdata['USERID']}
					data_json = json.dumps(data)
					conn_rec.send(data_json.encode())
					data_json = conn_rec.recv(1024).decode()
					token,response = self.parse_json(data_json)
					if(response=='0'):
						data = {'TOKEN': 'ADDF', 'SERVERDATA': {'TEXT': 'The user you are looking rejected chat request'}}
						data_json = json.dumps(data)
						conn.send(data_json.encode())
					else:
						data = {'TOKEN': 'ADDS', 'SERVERDATA':{'TEXT': 'The user added you', 'PUB_KEY': user_publickey[userdata['USERID']], 'USER_ID': userdata['USERID']}}
						data_json = json.dumps(data)
						conn.send(data_json.encode())
						data = {'TOKEN': 'ADDS', 'SERVERDATA': {'PUB_KEY': user_publickey[userid], 'TEXT': 'Public Key delivered', 'USER_ID': userid}}
						data_json = json.dumps(data)
						conn_rec.send(data_json.encode())
						friends[userid].append(userdata['USERID'])
						friends[userdata['USERID']].append(userid)

			# elif(token=='SFILE'):
			# 	if(userdata['RECV_ID'] not in user_conn_map.keys()):
			# 		data = {'TOKEN':'SFILE', 'SERVERDATA':{'SEND_ID': 'SERVER','RESPONSE': 0 ,'TEXT':'The user you are looking for is not online.'}}
			# 		data_json = json.dumps(data)
			# 		conn.send(data_json.encode())
			# 	else:
			# 		data = {'TOKEN':'SFILE', 'SERVERDATA':{'SEND_ID': 'SERVER','RESPONSE': 1 ,'TEXT':'Sending File'}}
			# 		data_json = json.dumps(data)
			# 		conn.send(data_json.encode())

			# 		conn_rec = user_conn_map[userdata['RECV_ID']]
			# 		data = {'TOKEN':'RFILE', 'SERVERDATA':{'SEND_ID': userid, 'TEXT':userdata['NAME']}}
			# 		data_json = json.dumps(data)
			# 		conn_rec.send(data_json.encode())

					

			elif(token=='END'):
				break

	def parse_json(self,data_json):
		data = ast.literal_eval(data_json)
		return data['TOKEN'], data['USERDATA']


def accept():
	threads = []
	while(True):
		print('Waiting for Connections')
		conn, addr = server_socket.accept()
		print("Connection from: " + str(addr))
		t = threading.Thread(target=client, args=(conn,addr,))
		threads.append(t)
		t.daemon = True
		t.start()
	for t in threads:
		t.join()

	server_socket.close()







builder = Gtk.Builder()
builder.add_from_file("interfaces/server_interface.glade")
builder.connect_signals(Handler())
print("Starting Server Interface GUI")
window = builder.get_object("main_window")
window.show_all()
print("abc")
Gtk.main()