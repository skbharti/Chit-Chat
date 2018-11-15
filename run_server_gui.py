import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


UNSUCCESSFUL = '[UNSUCCESSFUL]'
PASSWORD = '[PASSWORD]'
TOO = '[TOO]'

users = {'a':'a','b':'b'}
user_port_map = {}
user_conn_map = {}


class Handler:

	def start_server():
		# this gets executed when 'Start Server' button in Server interface is pressed. 
		pass

	def stop_server():
		# this gets executed when 'Stop Server' button in Server interface is pressed. 
		pass

	def quit_window():
		# this gets executed when 'Quit' button in File Menu is pressed. 
		print("Killing GUI")
		Gtk.main_quit()

host = socket.gethostname()
file = open("port.txt","r") 
port = int(file.read())+1
print("Port: ",port)
file.close()

file = open("port.txt","w") 
file.write(str(port))
file.close()

server_socket = socket.socket()
server_socket.bind((host, port))
server_socket.listen(5)

#########################################################
def client():
	while(True):
		data_json = conn.recv(1024).decode()
		token, userdata = parse_json(data_json)
		if(token=='AUTH'):
			userid = userdata['USERID']
			response = authenticate(userdata, addr, conn)
			if(response==1):
				data = {'TOKEN': 'SUCCESS', 'SERVERDATA': 'Authentication Successful'}
				data_json = json.dumps(data)
				conn.send(data_json.encode())
			else:
				data = {'TOKEN': 'UNSUCCESS', 'SERVERDATA': 'Authentication Unsuccessful'}
				data_json = json.dumps(data)
				conn.send(data_json.encode())

		elif(token=='SINGLECHAT'):
			# reject if user is not online  # threads are to be created to deal with it
			# accept and send if he is online
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
			# reject if no user in the group is online
			# accept and send to the group users online
			pass

		elif(token=='END'):
			break
########################################################

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



ta = threading.Thread(target=accept,args=())
ta.daemon = True
ta.start()



builder = Gtk.Builder()
builder.add_from_file("interfaces/server_interface.glade")
builder.connect_signals(Handler())
print("Starting Server Interface GUI")
window = builder.get_object("main_window")
window.show_all()

Gtk.main()