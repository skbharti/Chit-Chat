import gi
from run_chat_box import *

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

friend_publickey = {}


class Handler:
	userid = ''
	def user_login(self, button):
		# this gets executed when 'Log Me In!' button in User interface is pressed. 

		##### check if already logged in; if so display message


		##### if not open the chat box after authentication
		self.userid = builder.get_object('user_id_textbox').get_text()
		password = builder.get_object('password_textbox').get_text()
		data = {'TOKEN': 'AUTH', 'USERDATA': {'USERID': self.userid, 'PASSWORD': password}}
		data = json.dumps(data)
		# self.display(data)
		client_socket.send(data.encode())

		data_json = client_socket.recv(1024).decode()
	
		token, serverdata = self.parse_json(data_json)
		if(token=='SUCCESS'):
			window.destroy()
			builder.add_from_file("interfaces/chat_box.glade")
			builder.connect_signals(Handler())
			print("Starting Chat Box GUI")
			window2 = builder.get_object("main_window")
			window2.show_all()
			
			t = threading.Thread(target=self.recv, args=())
			t.daemon = True
			t.start()

		
	def recv(self):
		self.add_recipients()
		file = './'+self.userid+'.txt'
		f = open(file, 'r')
		privatekey_str = f.read()
		f.close()
		privatekey = privatekey_str.importKey()
		while(True):
			data_json = client_socket.recv(1024).decode()
			token, serverdata = self.parse_json(data)
			msg = privatekey.decrypt(ast.literal_eval(str(serverdata['TEXT'])))
			self.display(msg)

	def user_signup(self, button):
		# this gets executed when 'Sign Me Up!' button in User interface is pressed. 
		random_generator = Random.new().read
		key = RSA.generate(1024, random_generator)
		publickey_str = key.publickey().exportKey() # pub key export for exchange
		privatekey_str = key.exportKey()
		self.userid = builder.get_object('user_id_textbox').get_text()
		password = builder.get_object('password_textbox').get_text()
		data = {'TOKEN': 'SIGNUP', 'USERDATA': {'USERID': self.userid, 'PASSWORD': password, 'PUB_KEY': publickey_str}}
		data = json.dumps(data)
		client_socket.send(data.encode())
		print("data sent")
		data_json = client_socket.recv(1024).decode()
	
		token, serverdata = self.parse_json(data_json)
		if(token=='SUCESS'):
			file = './'+self.userid+'.txt'
			f = open(file, 'w')
			f.write(privatekey_str)
			f.close()
		print(serverdata)
		self.display(serverdata)
		pass

	def display(self, data):
		# this gets should be used to update textboxes
		# token, serverdata = self.parse_json(data)
		output_text_buffer = builder.get_object('main_display').get_buffer()
		output_text_buffer.set_text(data)

	def parse_json(self,data_json):
		data = ast.literal_eval(data_json)
		return data['TOKEN'], data['SERVERDATA']

	def send_message(self, button):

		#########
		# get userid
		########
		file = builder.get_object('file_chooser').get_filename()
		builder.get_object('file_chooser').unselect_all()
		
		# if(file!=None):
		# 	tdata = []
		# 	with open(file,"rb") as file:
		# 		while True:
		# 			dfile = file.read(500)
		# 			if not dfile:
		# 				break
		# 			tdata.append(dfile)

		# 	data = {'TOKEN': 'SFILE', 'USERDATA': {'RECV_ID': userid, 'NAME': os.path.basename(file)}}
		# 	data = json.dumps(data)
		# 	client_socket.send(data.encode())

		# 	data_json = client_socket.recv(1024).decode()
		# 	token, serverdata = self.parse_json(data_json)
		# 	self.display(serverdata['TEXT'])

		# 	if(serverdata['RESPONSE']==1):
		# 		i=0
		# 		while part in tdata:
		# 			i=i+1
		# 			data = {'TOKEN': 'PFILE', 'USERDATA': {'RECV_ID': userid, 'NAME': os.path.basename(file),'PART': part}}
		# 			data = json.dumps(data)
		# 			client_socket.send(data.encode())



		# 		data = {'TOKEN': 'FFILE', 'USERDATA': {'RECV_ID': userid, 'NAME': os.path.basename(file)}}
		# 		data = json.dumps(data)
		# 		client_socket.send(data.encode())

		# this gets executed when 'Send' button in Chat Box interface is pressed.
		# replace the code; currently just prints the input text to display
		input_text_buffer = builder.get_object('message_textbox').get_buffer()
		output_text_buffer = builder.get_object('main_display').get_buffer()
		input_text = input_text_buffer.get_text(input_text_buffer.get_start_iter(), input_text_buffer.get_end_iter(), True) 
		output_text = output_text_buffer.get_text(output_text_buffer.get_start_iter(), output_text_buffer.get_end_iter(), True) 
		output_text_buffer.set_text(output_text+'\n'+input_text)


		
	def add_recipient(self, button):
		input_text = builder.get_object('add_recipient_textbox').get_text()
		data = {'TOKEN': 'ADD', 'USERDATA': {'USERID': input_text}}
		data = json.dumps(data)
		client_socket.send(data.encode())
		data_json = client_socket.recv(1024).decode()
		token, serverdata = self.parse_json(data_json)
		self.display(serverdata)
		if(token == 'ADDS'):
			friend_publickey[input_text] = serverdata['PUB_KEY']
		####################
		# add to list
		####################

		print("added")
		
	
	def display_chat(self,data):
		# this gets should be used to update textboxes
		output_text_buffer = builder.get_object('main_display').get_buffer()
		output_text = output_text_buffer.get_text(output_text_buffer.get_start_iter(), output_text_buffer.get_end_iter(), True) 
		output_text_buffer.set_text(output_text+'\n'+input_text)
		
		pass

	def quit_window(self, button):
		print("Killing GUI")
		Gtk.main_quit()

	def recipient_changed(self,combo):
		tree_iter = combo.get_active_iter()
		if tree_iter is not None:
			model = combo.get_model()
			row_id, name = model[tree_iter][:2]
			print("Selected: ID=%d, name=%s" % (row_id, name))
		else:
			entry = combo.get_child()
			print("Entered: %s" % entry.get_text())

	def add_recipients(self):
		combobox = builder.get_object('recipient_dropdown')
		store = Gtk.ListStore(int,str)

		# put the code for actual list of recipients
		store.append ([1, "SKB"])
		store.append ([2, "AMS"])
		store.append ([3, "GSP"])

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