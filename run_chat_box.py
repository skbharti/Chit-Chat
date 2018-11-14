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

	def display_test():
		# this gets should be used to update textboxes
		pass

	def quit_window(self, button):
		# this gets executed when 'Quit' button in File Menu is pressed. 
		print("Killing GUI")
		Gtk.main_quit()

if __name__ == "__main__":
	builder = Gtk.Builder()
	# chat_box just for testing purpose; replace chat_box with client_interface
	builder.add_from_file("interfaces/chat_box.glade")
	builder.connect_signals(Handler())
	print("Starting GUI")
	window = builder.get_object("main_window")
	window.show_all()

	Gtk.main()

