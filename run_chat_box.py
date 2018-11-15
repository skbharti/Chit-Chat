import threading
import socket
import json
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Handler:

	def user_login():
		# this gets executed when 'Log Me In!' button in User interface is pressed. 
		pass

	def user_signup():
		# this gets executed when 'Sign Me Up!' button in User interface is pressed. 
		pass

	

	def quit_window(self, button):
		print("Killing GUI")
		Gtk.main_quit()


def recv():
	while(True):
		data_json = client_socket.recv(1024).decode()
		display(data_json)


if __name__ == "__main__":

	print("abba")
	builder = Gtk.Builder()
	# chat_box just for testing purpose; replace chat_box with client_interface
	builder.add_from_file("interfaces/chat_box.glade")
	builder.connect_signals(Handler())
	print("Starting GUI")
	window = builder.get_object("main_window")
	window.show_all()

	t = threading.Thread(target=recv, args=())
	t.daemon = True
	t.start()

	Gtk.main()

