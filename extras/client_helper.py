import socket
import json

msg_token = '<m>'

def send_message(senderid, receiverid, msg, client_socket):
	message = {}
	message['Token'] = msg_token
	data = {}
	data['SenderID'] = senderid
	data['ReceiverID'] = receiverid
	data['Message'] = msg
	message['Data'] = data
	msg_json = json.dumps(message)
	client_socket.send(msg_json.encode())
	
	