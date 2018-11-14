import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Handler:
	def onDestroy(self, *args):
		Gtk.main_quit()

	def onButtonPressed(self, button):
		print("Hello World!")

	def start_server():
		# this gets executed when 'Start Server' button in Server interface is pressed. 
		pass

	def stop_server():
		# this gets executed when 'Stop Server' button in Server interface is pressed. 
		pass

	def quit_window():
		# this gets executed when 'Quit' button in File Menu is pressed. 
		pass

builder = Gtk.Builder()
builder.add_from_file("interfaces/server_interface.glade")
builder.connect_signals(Handler())

window = builder.get_object("main_window")
window.show_all()

Gtk.main()