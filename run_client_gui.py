import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Handler:
	def onDestroy(self, *args):
		Gtk.main_quit()

	def onButtonPressed(self, button):
		print("Hello World!")

	def user_login():
		# this gets executed when 'Log Me In!' button in User interface is pressed. 
		pass

	def user_signup():
		# this gets executed when 'Sign Me Up!' button in User interface is pressed. 
		pass

	def send_message():
		# this gets executed when 'Send' button in Chat Box interface is pressed. 
		pass

	def add_recipient():
		# this gets executed when 'Add' button  for adding recipient in Chat Box interface is pressed. 
		pass

	def display_test():
		# this gets should be used to update textboxes
		pass

	def quit_window():
		# this gets executed when 'Quit' button in File Menu is pressed. 
		pass

builder = Gtk.Builder()
builder.add_from_file("interfaces/client_interface.glade")
builder.connect_signals(Handler())

window = builder.get_object("main_window")
window.show_all()

Gtk.main()