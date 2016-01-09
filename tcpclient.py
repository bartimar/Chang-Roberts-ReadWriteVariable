#!/usr/bin/python

import sys
import socket
import time
import string
import threading

nodes = []
end = False
sh_var = "default"
  

def broadcast(msg):
 for node in nodes:
   node.send(msg)

def unicast(msg):
 nodes[0].send(msg)
 
def client(dport):
 time.sleep(3)
 i=0;
 global sh_var
 global end
 clientsocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
 clientsocket.connect(('localhost', dport))
 nodes.append(clientsocket) 
 #clientsocket.connect(('localhost', 9001))
 #nodes.append(clientsocket) 

## LOGOUT NECHCI POSILAT VSEM!!!

 while end!=True:
   print 'c'
   s = raw_input('Choose one\n1 - print variable\n2 - set variable\n3 - logout\nyour choice: ');
   print 'ca'
   if s=="3":
      broadcast(s)
      print 'Client: end->True'
      end = True   
      break
   if s == "2":
      var =  raw_input('Insert new value: ')
      sh_var = var
      clientsocket.send(s + ' ' + var)
   else: clientsocket.send(s)
   if end == True:
      break
   buf = clientsocket.recv(64)
   print 'car'
   if len(buf) > 0:
     print buf
 clientsocket.close ()
 clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def server(sport):
 global end
 global sh_var
 serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 serversocket.bind(('localhost', sport))
 serversocket.listen(5) # become a server socket, maximum 5 connections

 connection, address = serversocket.accept()
 id=str(address[0])+':'+str(address[1])
 while end != True:
     print 's'
     buf = connection.recv(64)
     print 'as'
     if len(buf) > 0:
         r = buf[2:]
         if buf[0] == '2':
           print 'Changing variable '+ sh_var + '->' + r
           sh_var = r;
         if buf == '3': 
  	   print 'RECV:' + id + '> logout!'
 	   end = True
           print 'Server: end->True'
 	   break
         print 'RECV:'+ id + '> ' + buf
	 print 'ass'
	 connection.send('shared variable: ' + sh_var)
         #break


 serversocket.close()

if(len(sys.argv) != 3):
 print "Error: exactly 2 argument(s) expected!"
 exit()

sport = int(sys.argv[1])
dport = int(sys.argv[2])

# Create two threads as follows
try:
 c=threading.Thread( target=client, args=(dport,) )
 s=threading.Thread( target=server, args=(sport,) )
except (KeyboardInterrupt,SystemExit):
   print "Error: unable to start thread"
   sys.exit()

s.start()
time.sleep(4)
c.start()


