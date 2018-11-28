import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os
import getpass 
import socket
import ast
import threading
import json
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
import pickle

friend_publickey = {}

class Handler:
	user_data = {}
	def user_login(self, button):
		# this gets executed when 'Log Me In!' button in User interface is pressed. 

		##### check if already logged in; if so display message


		##### if not open the chat box after authentication
		input_user_id = builder.get_object('user_id_textbox').get_text()
		input_password = builder.get_object('password_textbox').get_text()
		data = {'TOKEN': 'AUTH', 'USERDATA': {'USERID': input_user_id, 'PASSWORD': input_password}}
		data = json.dumps(data)
		# self.display(data)
		client_socket.send(data.encode())

		data_json = client_socket.recv(1024).decode()
	
		token, serverdata = self.parse_json(data_json)
		if(token=='SUCCESS'):
			self.user_data = serverdata['USERDATA']
			self.save_user_data()
			window.destroy()
			builder.add_from_file("interfaces/chat_box.glade")
			builder.connect_signals(Handler())
			main_display = builder.get_object('main_display')
			main_heading = builder.get_object('main_heading')
			print('----------------------'+self.user_data['user_id']+'---------------------')
			main_heading.set_text('Welcome '+self.user_data['user_id']+' to Chit-Chat Application!')
			main_display.set_wrap_mode(1)
			print("Starting Chat Box GUI")
			window2 = builder.get_object("main_window")
			window2.show_all()
			self.display('You are successfully logged in now!')
			self.update_recipients_dropdown()
			
			t = threading.Thread(target=self.recv, args=())
			t.daemon = True
			t.start()
		else:
			self.display(serverdata['TEXT'])	

		

	def save_user_data(self):
		file = open('data/client/'+self.user_data['user_id']+'.pickle', 'wb')
		pickle.dump(self.user_data, file)
		file.close()

	def recv(self):
		while(True):
			data_json = client_socket.recv(1024).decode()
			token, serverdata = self.parse_json(data_json)

			if(token=='ADD_RECIPIENT_REQUEST_TO_RECIPIENT'):
				print("Recipient recieved request.")
				# dialog = Gtk.FileChooserDialog("Please choose a folder", None,Gtk.FileChooserAction.SELECT_FOLDER,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,"Select", Gtk.ResponseType.OK))
				# dialog.set_default_size(800, 400)

				# response = dialog.run()
				# if response == Gtk.ResponseType.OK:
				# 	print("Select clicked")
				# 	print("Folder selected: " + dialog.get_filename())
				# elif response == Gtk.ResponseType.CANCEL:
				# 	print("Cancel clicked")

				# dialog.destroy()

			if(token == 'ADD_SUCCESS_TO_SENDER'):
				self.display(serverdata['TEXT'])
				combobox = builder.get_object('recipient_dropdown')
				store = Gtk.ListStore(int,str)
				store.append([len(friend_publickey), serverdata['USER_ID']])
				combobox.connect('changed',self.recipient_changed)
				combobox.set_entry_text_column(1)
				cell = Gtk.CellRendererText()
				combobox.pack_start(cell,True)
				combobox.add_attribute(cell, 'text', 0)
				combobox.set_model(store)
				combobox.set_active(0)


			if(token == 'ADD_FAIL_TO_SENDER'):
				self.display(serverdata['TEXT'])	

			
			if(token=='SINGLECHAT'):
				# msg = privatekey.decrypt(ast.literal_eval(str(serverdata['TEXT'])))
				msg = serverdata['TEXT']
				print("here")
				self.display('from  '+serverdata['SEND_ID']+' : '+msg)

			if(token=='BROADCAST'):
				# msg = privatekey.decrypt(ast.literal_eval(str(serverdata['TEXT'])))
				msg = serverdata['TEXT']
				self.display('broadcast from  '+serverdata['SEND_ID']+' : '+msg)

	def accept_request(self, button):
		data = {'TOKEN': 'ADDSUCCESS', 'RESPONSE': '1'}
		data_json = json.dumps(data)
		client_socket.send(data_json)


	def reject_request(self, button):
		data = {'TOKEN': 'ADDF', 'RESPONSE': '0'}
		data_json = json.dumps(data)
		client_socket.send(data_json)
			
	def update_recipient_list(recp_id):
		self.user_data['recipient_list'].append(recp_id)
		self.update_recipients_dropdown()


	def user_signup(self, button):
		input_user_id = builder.get_object('user_id_textbox').get_text()
		input_password = builder.get_object('password_textbox').get_text()
		# data = {'TOKEN': 'SIGNUP', 'USERDATA': {'USERID': self.userid, 'PASSWORD': password, 'PUB_KEY': publickey_str.decode('utf8')}}
		data = {'TOKEN': 'SIGNUP', 'USERDATA': {'USERID': input_user_id, 'PASSWORD': input_password}}

		data = json.dumps(data)
		client_socket.send(data.encode())
		print("data sent")
		data_json = client_socket.recv(1024).decode()
	
		token, serverdata = self.parse_json(data_json)
		if(token=='SUCCESS'):
			print("User SignUp Success!")
			builder.get_object('user_id_textbox').set_text('')
			builder.get_object('password_textbox').set_text('')
		self.display(serverdata['TEXT'])

	def display(self, data):
		# this gets should be used to update textboxes
		output_text_buffer = builder.get_object('main_display').get_buffer()
		output_text_buffer.insert_at_cursor(data+'\n')

	def parse_json(self,data_json):
		data = ast.literal_eval(data_json)
		return data['TOKEN'], data['SERVERDATA']

	def send_message(self, button):
		combo = builder.get_object('recipient_dropdown')
		tree_iter = combo.get_active_iter()
		if tree_iter is not None:
			model = combo.get_model()
			row_id, recvid = model[tree_iter][:2]
		print(recvid)


		input_text_buffer = builder.get_object('message_textbox').get_buffer()
		input_text = input_text_buffer.get_text(input_text_buffer.get_start_iter(), input_text_buffer.get_end_iter(), True) 
		self.display('to '+recvid+' : '+input_text)

		print("broadcasting")
		if(recvid=='broadcast'):
			data = {'TOKEN': 'BROADCAST', 'USERDATA': {'RECV_ID': recvid, 'TEXT': input_text}}
		else:
			data = {'TOKEN': 'SINGLECHAT', 'USERDATA': {'RECV_ID': recvid, 'TEXT': input_text}}
		
		data = json.dumps(data)
		input_text_buffer.set_text('')
		client_socket.send(data.encode())
	
	def display_chat(self,data):
		# this gets should be used to update textboxes
		output_text_buffer = builder.get_object('main_display').get_buffer()
		output_text = output_text_buffer.get_text(output_text_buffer.get_start_iter(), output_text_buffer.get_end_iter(), True) 
		output_text_buffer.set_text(output_text+'\n'+input_text)
		
	def quit_window(self, button):
		print("Killing GUI")
		# with open(self.userid+".pkl", "wb") as handle:
		# 	pickle.dump(friend_publickey,handle)
		client_socket.close()
		Gtk.main_quit()

	def add_recipient(self, button):
		input_text = builder.get_object('add_recipient_textbox').get_text()
		data = {'TOKEN': 'ADD_RECIPIENT_REQUEST_BY_SENDER', 'USERDATA': {'USERID': input_text}}
		data = json.dumps(data)
		client_socket.send(data.encode())

	def recipient_changed(self,combo):
		tree_iter = combo.get_active_iter()
		if tree_iter is not None:
			model = combo.get_model()
			row_id, name = model[tree_iter][:2]
			print("Selected: ID=%d, name=%s" % (row_id, name))
		else:
			entry = combo.get_child()
			print("Entered: %s" % entry.get_text())

	def update_recipients_dropdown(self):
		group_list = {'group:g1':['aa','bb'],'group:g2':['bb','cc'],'group:g3':['cc','zz']}
		combobox = builder.get_object('recipient_dropdown')
		store = Gtk.ListStore(int,str)
		print(self.user_data['recipient_list'])
		i=1
		for fid in self.user_data['recipient_list']:
			store.append([i, fid])
			i = i+1
		for gid in group_list.keys():
			print(gid)
			store.append([i, gid])
			i=i+1

		# the function recipient_change
		combobox.connect('changed',self.recipient_changed)
		combobox.set_entry_text_column(1)
		cell = Gtk.CellRendererText()
		combobox.pack_start(cell,True)
		combobox.add_attribute(cell, 'text', 0)
		combobox.set_model(store)
		combobox.set_active(0)




UNSUCCESSFUL = '[UNSUCCESSFUL]'
PASSWORD = '[PASSWORD]'
TOO = '[TOO]'
USERID = ''

host = socket.gethostname()
file = open("port.txt","r") 
port = int(file.read())
print("Port: ",port)
file.close()
	
client_socket = socket.socket()
client_socket.connect((host, port))

builder = Gtk.Builder()
# chat_box just for testing purpose; replace chat_box with client_interface
builder.add_from_file("interfaces/client_interface.glade")
builder.connect_signals(Handler())
print("Starting Client Interface GUI")
window = builder.get_object("main_window")
# add_recipients()
window.show_all()

Gtk.main()