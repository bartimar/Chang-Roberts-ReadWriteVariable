#!/usr/bin/python

import sys
import socket
import time
import string
import threading

def client(dPort):
 time.sleep(3)
 i=0;
 clientsocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
 clientsocket.connect(('localhost', dPort))

 while True:
   s = raw_input('Choose one\n1 - print variable\n2 - set variable\n3 - logout\nyour choice: ');
   if s=="3":
      break
   if s == "2":
      var =  raw_input('Insert new value: ')
      clientsocket.send(s + ' ' + var)
   else: clientsocket.send(s)
   buf = clientsocket.recv(64)
   if len(buf) > 0:
     print buf
 clientsocket.close ()
 clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


if(len(sys.argv) != 2):
 print "Error: exactly 2 arguments expected!"
 exit()

myport = int(sys.argv[1])

# Create two threads as follows
try:
   t=threading.Thread( target=client, args=(myport,) )
except:
   print "Error: unable to start thread"

# SERVER
t.start()

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', myport))
serversocket.listen(5) # become a server socket, maximum 5 connections
sh_var = "default"

connection, address = serversocket.accept()
id=str(address[0])+':'+str(address[1])
while True:
    buf = connection.recv(64)
    if len(buf) > 0:
        print 'RECV:'+ id + '> ' + buf
        r = buf[2:]
        if buf[0] == '2':
          print 'Changing variable '+ sh_var + '->' + r
          sh_var = r;
        connection.send('shared variable: ' + sh_var)
        #break
