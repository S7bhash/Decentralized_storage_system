import socket,json,base64

def client():
	connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	connection.connect(("192.168.43.185",12345))
	#dictionary = {"command":command,"name":name,"shape":command,"image":image_data}
	#json_data=json.dumps(dictionary)
	#connection.send(bytes(json_data,"utf-8"))

client()
