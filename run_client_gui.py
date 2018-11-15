import gi
from run_chat_box import *
import json

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Handler:

	def user_login(self, button):
		# this gets executed when 'Log Me In!' button in User interface is pressed. 

		##### check if already logged in; if so display message


		##### if not open the chat box after authentication
		userid = builder.get_object('user_id_textbox').get_text()
		password = builder.get_object('password_textbox').get_text()
		data = {'TOKEN': 'AUTH', 'USERDATA': {'USERID': userid, 'PASSWORD': password}}
		# self.display(data)
		data_json = json.dumps(data)
		client_socket.send(data_json.encode())

		data_json = client_socket.recv(1024).decode()
	
		token, serverdata = parse_json(data_json)
		if(token=='SUCCESS'):
		##### authentication
		##### open chat box if authentication success
			builder.add_from_file("interfaces/chat_box.glade")
			builder.connect_signals(Handler())
			print("Starting Chat Box GUI")
			window = builder.get_object("main_window")
			window.show_all()
		

	def user_signup(self, button):
		# this gets executed when 'Sign Me Up!' button in User interface is pressed. 
		pass

	def display(self, data):
		# this gets should be used to update textboxes
		print(data)
		pass

	def send_message(self, button):
		# this gets executed when 'Send' button in Chat Box interface is pressed.
		# replace the code; currently just prints the input text to display
		input_text_buffer = builder.get_object('message_textbox').get_buffer()
		output_text_buffer = builder.get_object('main_display').get_buffer()
		input_text = input_text_buffer.get_text(input_text_buffer.get_start_iter(), input_text_buffer.get_end_iter(), True) 
		output_text = output_text_buffer.get_text(output_text_buffer.get_start_iter(), output_text_buffer.get_end_iter(), True) 
		output_text_buffer.set_text(output_text+'\n'+input_text)
		
	def add_recipient(self, button):
		# this gets executed when 'Add' button  for adding recipient in Chat Box interface is pressed. 
		pass

	def quit_window(self, button):
		# this gets executed when 'Quit' button in File Menu is pressed. 
		print("Killing GUI")
		Gtk.main_quit()

builder = Gtk.Builder()
# chat_box just for testing purpose; replace chat_box with client_interface
builder.add_from_file("interfaces/client_interface.glade")
builder.connect_signals(Handler())
print("Starting Client Interface GUI")
window = builder.get_object("main_window")
window.show_all()

Gtk.main()

