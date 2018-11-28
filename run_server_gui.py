import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import pickle
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
conn_user_map = {}

friends = {}
user_publickey = {}


class Handler:
	server_socket = 0
	state = 0
	user_data = {}
	def start_server(self,button):
		if(self.state):
			self.display("Server already Online.")
			return

		self.server_socket = socket.socket()
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
		self.display("Server Started")
		self.state = 1
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

	def stop_server(self,button):
		if(self.state == 1):
			self.server_socket.close()
			self.display("Server Stopped.")
			self.state = 0
		else:
			self.display("Server already Offline.")

	def display(self, input_text):
		output_text_buffer = builder.get_object('server_main_display_textbox').get_buffer()
		output_text_buffer.insert_at_cursor(input_text+'\n')

	def create_user_data(self,user_id):
		user_data = {}
		user_data['user_id']=user_id
		user_data['recipient_list']={'aa':'123','bb':'123','cc':'123','zz':'123','broadcast':'123'}
		user_data['groups_list']=[]

		file = open('data/server/'+user_id+'.pickle', 'wb')
		pickle.dump(user_data, file)
		file.close()

	def save_user_data(self,user_data):
		file = open('data/server/'+user_data['user_id']+'.pickle', 'wb')
		pickle.dump(user_data, file)
		file.close()

	def update_user_data(self,user_id, recp_id):
		file = open('data/server/'+user_id+'.pickle', 'rb')
		user_data = pickle.load(file)
		file.close()
		user_data['recipient_list'].extend([recp_id])
		file = open('data/server/'+user_id+'.pickle', 'rb')
		pickle.dump(user_data, file)
		file.close()

	def load_user_data(self,user_id):
		file = open('data/server/'+user_id+'.pickle', 'rb')
		user_data = pickle.load(file)
		file.close()
		return user_data

	def quit_window(self, button):
		# this gets executed when 'Quit' button in File Menu is pressed. 
		print("Killing GUI")
		Gtk.main_quit()

	def authenticate(self,data,addr,conn):
		userid = data['USERID']
		password = data['PASSWORD']
		user_port_map[userid] = addr[1]
		user_conn_map[userid] = conn
		conn_user_map[conn] = userid

		file = open('data/server/serverfile.pickle', 'rb')
		server_data = pickle.load(file)
		file.close()

		auth_data = server_data['auth_list']
		if(userid in list(auth_data.keys())):
			if(password == auth_data[userid]):
				print('user in the list')
				return 1
		return 0
		# f = open(serverfile, 'r')
		# # print("opened")
		# # print(userid)
		# # print(password)
		# for line in f:
		# 	value = line.split(',')
		# 	# print(value[0], value[1])
		# 	if(value[0]==userid):
		# 		if(password==value[1][:-1]):
		# 			f.close()
		# 			return 1			

		return 0	

	def client(self,conn,addr):
		while(True):
			data_json = conn.recv(1024).decode()
			token, userdata = self.parse_json(data_json)
			if(token=='AUTH'):
				userid = userdata['USERID']
				response = self.authenticate(userdata, addr, conn)
				if(response==1):
					user_data = self.load_user_data(userid)
					data = {'TOKEN': 'SUCCESS', 'SERVERDATA':{'TEXT': 'Authentication Successful', 'USERDATA':user_data}}
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
				# publickey_str = userdata['PUB_KEY']
				file = open('data/server/serverfile.pickle', 'rb')
				server_data = pickle.load(file)
				user_list = server_data['auth_list'].keys()
				# f = open(serverfile, 'r')
				# for line in f:
				# 	value = line.split(',')
				# 	if(value[0]==userid):
				# 		flag = 1
				# 		break
				file.close()
				print('here')
				if(userid in user_list):
					data = {'TOKEN': 'UNSUCCESS', 'SERVERDATA':{'TEXT': 'Signup Unsuccessful, username already exists.'}}
					data_json = json.dumps(data)
					conn.send(data_json.encode())
				else:
					file = open('data/server/serverfile.pickle', 'wb')
					server_data['auth_list'][userid]=password
					pickle.dump(server_data, file)
					file.close()
					# user_publickey[userid] = publickey_str.encode('utf8')
					data = {'TOKEN': 'SUCCESS', 'SERVERDATA':{'TEXT': 'Signup Successful.'}}
					self.create_user_data(userid)
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

			elif(token=='BROADCAST'):
				for um in user_conn_map.keys():
					conn_rec = user_conn_map[um]
					data = {'TOKEN':'BROADCAST', 'SERVERDATA':{'SEND_ID': userid, 'TEXT':userdata['TEXT']}}
					data_json = json.dumps(data)
					conn_rec.send(data_json.encode())	
				
			elif(token=='GROUPCHAT'):
				pass

			elif(token=='ADD_RECIPIENT_REQUEST_BY_SENDER'):
				print("Server recieved request")
				if(userdata['USERID'] not in user_conn_map.keys()):
					data = {'TOKEN':'ADDFAIL', 'SERVERDATA': {'TEXT': 'The user you are looking for is not online.'}}
					data_json = json.dumps(data)
					conn.send(data_json.encode())
				else:
					conn_rec = user_conn_map[userdata['USERID']]
					print("Server forwarding request.")
					data = {'TOKEN': 'ADD_RECIPIENT_REQUEST_TO_RECIPIENT', 'SERVERDATA': userdata['USERID']}
					data_json = json.dumps(data)
					conn_rec.send(data_json.encode())
					data_json = conn_rec.recv(1024).decode()
					token,response = self.parse_json(data_json)
					if(response=='0'):
						data = {'TOKEN': 'ADD_FAIL_TO_SENDER', 'SERVERDATA': {'TEXT': 'The user you are looking rejected chat request'}}
						data_json = json.dumps(data)
						conn.send(data_json.encode())
					else:
						data = {'TOKEN': 'ADD_SUCCESS_TO_SENDER', 'SERVERDATA':{'TEXT': 'The user approved your request.', 'USER_ID': userdata['USERID']}}

						# data = {'TOKEN': 'ADDS', 'SERVERDATA':{'TEXT': 'The user added you', 'PUB_KEY': user_publickey[userdata['USERID']], 'USER_ID': userdata['USERID']}}
						data_json = json.dumps(data)
						conn.send(data_json.encode())
						self.update_user_data(conn_user_map[userid], userdata['USERID'])
						# data = {'TOKEN': 'ADDS', 'SERVERDATA': {'TEXT': 'Public Key delivered', 'USER_ID': userid}}
						# data_json = json.dumps(data)
						# conn_rec.send(data_json.encode())
						# friends[userid].append(userdata['USERID'])
						# friends[userdata['USERID']].append(userid)

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