#!/usr/bin/python

import sys
import socket
import time
import string
import threading
import select 

connections = []
end = False
nodes = []
sh_var = "default"
hellomsg = ""
myIP = ''
myPort = -1
pongs = []

def addNode(node):
 global pongs
 node = node.split(' ')
 while len(node)>0:
   ip = node[0]
   port = node[1]
   node = node[2:]
   mnode = ip + ' ' + port
   print 'adding node ' + mnode
   if mnode not in nodes:
     print myIP+':'+str(myPort)+' '+ip+':'+port
     if myIP==ip and str(myPort)==port: continue 
     nodes.append(mnode)
     addConn(mnode)
     pongs = [0]*len(nodes)
 print 'currently have ' + str(len(nodes)) + ' nodes'
 #TODO sort
 
def deleteNode(node):
 print 'deleting node ' + node
 id = nodes.index(node)
 connections[id].close()
 del connections[id]
 nodes.remove(node)
 
def deleteConn(toDel):
 print 'deleting conn ' + toDel
 for conn in connections:
  host, port = conn.getsockname()
  bhost, bport = toDel.split(' ')
  if host == bhost and port ==bport :
    connections.remove(node)
    conn.close()
    print 'deleted'
    return 

def addConn(node):
 #TODO dont add myself
 node = node.split(' ')
 while len(node)>0:
  ip = node[0]
  port = node[1]
  node = node[2:]
  print 'adding conn ' + ip + ' ' + port
  clientsocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
  clientsocket.connect((ip,int(port)))
  if clientsocket not in connections:  connections.append(clientsocket)
  print 'currently have ' + str(len(connections)) + ' connections'
 #TODO sort

def printNodes():
 print '------------------------------'
 print myIP, myPort, '(me)'
 for node in nodes:
  print str(node)
 print 'total=' + str(len(nodes)+1)
 print '------------------------------'

def broadcast(msg):
 for i,conn in enumerate(connections):
   conn.send(msg)
   print "Send me->" + str(nodes[i]) + " (" + msg + ")"

def sendNodes(remote):
 if remote.count(' ')>2: return
 id = nodes.index(remote)
 conn = connections[id]
 msg = 'HELLO'
 for node in nodes:
  #conn.send('HELLO ' + node + ' ')
  msg += ' ' + node
 conn.send(msg)  

#def unicast(msg):
# if(len(connections)>0): 
#  connections[0].send(msg)
#  print "Send me->" + str(connections[0].getsockname()) + " (" + msg + ")"

def client(destIP, dport):
 global hellomsg
 #time.sleep(1)
 i=0;
 global sh_var
 global end
 print "dport=" + str(dport)
 clientsocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
 if(dport != -1):
  addNode(destIP + ' ' + str(dport))
  broadcast(hellomsg)
## LOGOUT NECHCI POSILAT VSEM!!!

 while end!=True:
   #print 'c'
   s = raw_input('Choose one\n1 - print variable\n2 - set variable\n3 - logout\n4 - check system\nyour choice: ');
   #print 'ca'
   if s=="3": #LOGOUT
      broadcast('BYE '+ hellomsg.split(' ',1)[1])
      print 'Client: end->True'
      end = True   
      break
   elif s == "2": # SET VAR
      var =  raw_input('Insert new value: ')
      sh_var = var
      broadcast('SET ' + sh_var)
   elif s == "1": # READ VAR
      print('shared variable: ' + sh_var)
   elif s == "4": # check system
      printNodes()
   else: 
      print 'wrong command \"'+ s + '\"!'
      continue
 clientsocket.close ()

def printUsage(args):
 print "USAGE: " + args[0] + " portToListen [neighborIP:neighborPort]"
 print "Please use ports >1023."
 exit()

def handlePong(node):
 id=nodes.index(node)
 #print 'id=' + str(id)
 pongs[id]+=1
 print 'pongs='+ str(pongs)
 m=max(pongs)
 for i,pong in enumerate(pongs):
  if(pong<m-2):
   node = nodes[i]
   print 'ALERT! node=' + node + ' is dead'
   deleteNode(node)
   del pongs[i]

def server(sport):
 global end
 global sh_var
 serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 serversocket.bind(('localhost', sport))
 serversocket.listen(10) # become a server socket, maximum 5 connections

 #connection, address = serversocket.accept()
 #id=str(address[0])+':'+str(address[1])
 read_list = [serversocket]
 timeout = 1
 cnt = 0
 while end != True:
  readable, writable, errored = select.select(read_list, [], [],timeout)
  #print 'readable=' + str(len(readable)) + ' writable=' + str(len(writable)) + ' errored=' + str(len(errored))
  if(len(readable)>0): cnt=0
  cnt+=1
  #print 'increm cnt='+str(cnt) + ', len=' + str(len(nodes))
  #if len(nodes) == 1 and cnt>6:
  # print 'ALERT! node=' + nodes[0] + ' is dead'
  # deleteNode(nodes[0])
  # del pongs[0]
 
  for s in readable:
    if s is serversocket: 
     connection, address = serversocket.accept()
     read_list.append(connection)
     print "Connection from ", str(connection.getsockname())  
    else:
     id=str(s.getsockname())
     #print 's'
     buf = connection.recv(64)
     #print 'as'
     if len(buf) > 0:
	 parse = buf.split(' ',1)
	 cmd = parse[0]
	 if cmd == 'SET':
	   #if(len(parse)<=2):
		#print "Wrong syntax.\nEnter value!"
		#continue
	   arg = parse[1]
	   print 'Changing variable '+ sh_var + '->' + arg
	   sh_var = arg;
	 if cmd == '3': 
	   print 'RECV:' + id + '> logout!'
	   end = True
	   print 'Server: end->True'
	   break
	 if cmd == 'HELLO':
	   #print 'server received hello via ' +  str(connection.getsockname())
	   #clientsocket.connect(s)
	   if buf == hellomsg:
	    continue
	   broadcast(buf)
	   addNode(parse[1])
	   sendNodes(parse[1])
	 if cmd == 'BYE':
	   print 'received BYE from ' + parse[1]
	   deleteConn(parse[1])
	   deleteNode(parse[1])
	   read_list.remove(connection)
	   continue
	 if cmd == 'PONG':
	   #print 'received pong from ' + parse[1]
	   handlePong(parse[1])
	   cnt=0
	 print 'RECV:'+ id + '> ' + buf
	 #print 'ass'
	 connection.send('shared variable: ' + sh_var)
	 #break
  
 serversocket.close()

def ping():
 while True:
  #for node in nodes:
  # pingsocket = socket.socket(
  #   socket.AF_INET, socket.SOCK_STREAM)
  # try:
  #   ip, port = node.split(' ')
  #   pingsocket.connect((ip,int(port)))
  # except: # if failed to connect
  #   print("Server "+ node + " offline: ")    # it prints that server is offline
  #   deleteNode(node)
  #   pingsocket.close()                  #closes socket, so it can be re-used
  # pingsocket.send('PONG ' + myIP + str(myPort))
  time.sleep(2)
  for conn in connections:
   #conn.send('PONG ' + myIP + ' '+ str(myPort))	    
   pass


######## MAIN ##########
argc = len(sys.argv)
if not (2 <= argc <= 3 ):
 printUsage(sys.argv)

sport = int(sys.argv[1])
if(argc > 2):
 neighbor = sys.argv[2].split(':') 
 if(len(neighbor)<2):
  printUsage(sys.argv)
 destIP = neighbor[0]
 dport = int(neighbor[1])
 if(dport<1024):
  printUsage(sys.argv)
else: 
  dport = -1
  destIP = "-1"

#TODO
hellomsg='HELLO '+ '127.0.0.1 ' + str(sport)
myIP = '127.0.0.1'
myPort = sport


# Create two threads as follows
try:
 c=threading.Thread( target=client, args=(destIP,dport,) )
 s=threading.Thread( target=server, args=(sport,) )
 p=threading.Thread( target=ping, args=() )

except (KeyboardInterrupt,SystemExit):
   print "Error: unable to start thread"
   sys.exit()


s.start()
time.sleep(1)
c.start()
p.start()

