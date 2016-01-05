import socket
import string

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', 8089))
serversocket.listen(5) # become a server socket, maximum 5 connections
sh_var = "default"

connection, address = serversocket.accept()

while True:
    buf = connection.recv(64)
    if len(buf) > 0:
        print address[0],':',address[1],'>', buf
	r = buf[2:]
	if buf[0] == '2':
	  print 'Changing variable '+ sh_var + '->' + r 
	  sh_var = r;
        connection.send('shared variable: ' + sh_var)
        #break
