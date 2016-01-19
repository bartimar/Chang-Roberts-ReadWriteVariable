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
leader = -1
logtime = 0 

def addNode(node):
 #info('adding node:' + node)
 global pongs
 global nodes
 node = node.split(' ')
 while len(node)>1:
   ip = node[0]
   port = node[1]
   node = node[2:]
   mnode = ip + ' ' + port
   info('adding node ' + mnode)
   if mnode not in nodes:
     info('node appended, connection created')
     nodes.append(mnode)
     if myIP==ip and myPort==int(port): continue 
     addConn(mnode)
     pongs = [0]*len(nodes)
 info('currently have ' + str(len(nodes)) + ' nodes')
 nodes = sorted(nodes)
 #TODO sort
 
def deleteNode(node):
 id = nodes.index(node)
 info('deleting node ' + node+' id='+str(id))
 #connections[id].close()
 #del connections[id]
 nodes.remove(node)
 if id==leader and getMyID()==(id-1)%len(nodes):
  info('leader left, starting new election')
  
 
def deleteConn(toDel):
 info('deleting conn ' + toDel)
 for conn in connections:
  host, port = conn.getpeername()
  bhost, bport = toDel.split(' ')
  info(host+'=='+bhost+' '+str(port)+'=='+bport)
  if host == bhost and port ==int(bport) :
    connections.remove(conn)
    conn.close()
    info('deleted')
    return 

def addConn(node):
 #TODO dont add myself
 node = node.split(' ')
 while len(node)>1:
  ip = node[0]
  port = node[1]
  node = node[2:]
  if ip==myIP and int(port)==myPort: continue
  info('adding conn ' + ip + ' ' + port)
  clientsocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
  clientsocket.connect((ip,int(port)))
  connections.append(clientsocket)
  clientsocket.send('WELCOME ' +myIP+' ' +str(myPort)+'\n')
  info('currently have ' + str(len(connections)) + ' connections')
 #TODO sort

def printNodes():
 info('------------------------------')
 #info(myIP + ':' + str(myPort) + ' (me)')
 for i,node in enumerate(nodes):
  ld=""
  if i==leader: ld=" = leader"
  if i==getMyID(): info(str(node) + '(me)'+ld)
  else: info(str(node)+ld)
 info('total=' + str(len(nodes)))
 info('------------------------------')

def sendLeft(msg):
 myIndex=getMyID()
 leftNode=(myIndex-1)%len(nodes)
 info('Sending to left node ('+ str(myIndex)+'->'+str(leftNode) +') '+ msg)
 left=nodes[leftNode].split(' ')
 for conn in connections:
  ip, port = conn.getpeername()
  if ip==left[0] and port==int(left[1]):
     info('really sending that msg')
     conn.send(msg+'\n')

def getMyID():
  return nodes.index(myIP +' '+str(myPort))

def sendToLeader(msg):
 info('sending to leader: '+msg)
 if leader==getMyID(): 
   broadcast(msg)
   return
 lead=nodes[leader].split(' ')
 for conn in connections:
   ip, port = conn.getpeername()
   if ip==lead[0] and port==int(lead[1]):
      conn.send(msg+'\n') 

def broadcast(msg):
 info('len conn='+ str(len(connections)))
 for conn in connections:
   conn.send(msg+'\n')
   info("Send me->" + str(conn.getpeername()) + " (" + msg + ")")

def isMe(node):
 spl = node.split(' ')
 ip = spl[0]
 port = spl[1]
 #info('to cmp: '+ip+'=='+myIP+' and '+port+'=='+str(myPort))
 if(ip == myIP) and (port==str(myPort)):
  return True
 return False

def isRemote(a,b):
 a = a.split(' ')
 b = b.split(' ')
 if(a[0]==b[0])and(a[1]==b[1]):
  return True
 return False

def sendNodes(remote):
 if remote.count(' ')>2: return
 id = nodes.index(remote)
 conn = connections[id]
 msg = 'WELCOME'
 for node in nodes:
  if(isMe(node)): continue
  #if(isRemote(remote,node)): continue
  #conn.send('HELLO ' + node + ' ')
  msg += ' ' + node
 #info('remote:' + remote + ' msg:' + msg)
 conn.send(msg+'\n') 
 info("Send me->" + str(nodes[id]) + " (" + msg + ")")
 if sh_var != 'default': 
  conn.send('SET ' + sh_var+'\n')
  info('send: SET ' + sh_var) 

def info(msg):
 global log
 global logtime
 print str(logtime)+': ' + msg
 log.write(str(logtime) +': '+msg + '\n')
 log.flush()

def client(destIP, dport):
 global hellomsg
 global leader
 #time.sleep(1)
 i=0;
 global sh_var
 global end
 info("dport=" + str(dport))
 addNode(myIP + ' ' +str(myPort))
 clientsocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
 if(dport != -1):
   addNode(destIP + ' ' + str(dport))
   broadcast(hellomsg)
   time.sleep(1)
   startVoting()
 else: 
   info("First node started on port " + str(myPort))
   leader=getMyID()
 while end!=True:
   #print 'c'
   s = raw_input('Choose one\n1 - print variable\n2 - set variable\n3 - logout\n4 - check system\nyour choice: ');
   #print 'ca'
   if s=="3": #LOGOUT
      broadcast('BYE '+ hellomsg.split(' ',1)[1])
      info('Client: end->True')
      end = True   
      break
   elif s == "2": # SET VAR
      var =  raw_input('Insert new value: ')
      sh_var = var
      sendToLeader('SET ' + sh_var)
   elif s == "1": # READ VAR
      info('shared variable: ' + sh_var)
   elif s == "4": # check system
      printNodes()
   else: 
      info('wrong command \"'+ s + '\"!')
      continue
 info('closing clientsocket')
 clientsocket.close ()

def printUsage(args):
 print("USAGE: " + args[0] + " IP:portToListen [neighborIP:neighborPort]")
 print("Please use ports >1023.")
 exit()

def handlePong(node):
 id=nodes.index(node)
 #print 'id=' + str(id)
 pongs[id]+=1
 info('pongs='+ str(pongs))
 m=max(pongs)
 for i,pong in enumerate(pongs):
  if(pong<m-2):
   node = nodes[i]
   info('ALERT! node=' + node + ' is dead')
   deleteNode(node)
   del pongs[i]

def endVote():
 sendLeft('ELECTED ' + str(getMyID()))

def vote(actual):
 if int(actual) < getMyID(): sendLeft('ELECTION '+str(getMyID()))
 else: sendLeft('ELECTION '+actual)

def startVoting():
 info('Voting initiated by node '+ str(getMyID()))
 vote('-1')

def server(sport):
 global end
 global sh_var
 global leader
 serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 serversocket.bind(('localhost', sport))
 serversocket.listen(10) # become a server socket, maximum 5 connections
 read_list = [serversocket]
 timeout = 1
 cnt = 0
 while end != True:
  readable, writable, errored = select.select(read_list, [], [])
  if(len(readable)>0): cnt=0
  cnt+=1
  for s in readable:
    if s is serversocket:
     connection, address = serversocket.accept()
     read_list.append(connection)
     info("Received new connection")
    else:
     id=str(s.getsockname())
     #info('Server is about to receive data')
     

     try:
       buf = s.recv(1024)
     except socket.error, e:
       err = e.args[0]
       if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
         sleep(1)
         print 'No data available'
         continue
       else:
          # a "real" error occurred
          print e
          sys.exit(1)

     buf = buf.rstrip() # remove trailing whitespaces
     #print 'as'
     lines=buf.split('\n') #receiveing more cmds because of tcp
     for line in lines:
	 
	 parse = line.split(' ',1)
	 cmd = parse[0]
	 if cmd == 'SET':
	   arg = parse[1]
	   info('Changing variable '+ sh_var + '->' + arg)
	   sh_var = arg;
	   if leader==getMyID(): broadcast(line) #I'm the leader, tell others the shared val
	 if cmd == '3': 
	   info('RECV:' + id + '> logout!')
	   end = True
	   info('Server: end->True')
	   break
	 if cmd == 'HELLO':
	   addNode(parse[1])
	   sendNodes(parse[1])
	   broadcast(line.replace('HELLO','WELCOME'))
           time.sleep(1)
           startVoting()
	   #TODO: set var to remote initial value
	 if cmd == 'WELCOME':
	   #info('got welcome msg: ' + line)
	   addNode(parse[1])
	 if cmd == 'BYE':
	   info('received BYE from ' + parse[1])
	   deleteConn(parse[1])
	   deleteNode(parse[1])
	   read_list.remove(s)
           startVoting()
	   continue
	 if cmd == 'ELECTION':
	   #info('Received ELECTION'+parse[1]+' =='+str(getMyID()))
           if int(parse[1])==getMyID():
	     info('I\'m the new leader.')
	     leader=int(getMyID())
             endVote()
	   else:
	     vote(parse[1])
	 if cmd == 'ELECTED':
	   info('Received ELECTED '+ parse[1])
           if int(parse[1]) != getMyID():
	     leader=int(parse[1])
	     info('System has a new leader: id='+str(leader))
	     sendLeft(line) 
	 if cmd == 'PONG':
	   #info('received pong from ' + parse[1])
	   handlePong(parse[1])
	   cnt=0
  
 info('Server terminating')
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

def timer():
 global logtime
 while True:
  time.sleep(1)
  logtime+=1

######## MAIN ##########
argc = len(sys.argv)
if not (2 <= argc <= 3 ):
 printUsage(sys.argv)
try:
 me = sys.argv[1].split(':')
 myIP=me[0]
 sport = int(me[1])

except:
 print("Error: First argument should be IP:port (including the semicolon)")
 printUsage(sys.argv)
 sys.exit()

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
hellomsg='HELLO '+ myIP + ' ' + str(sport)
myPort = sport

filename = 'dsv-' + myIP + '-' +str(sport) + '.log'
global log
log = open(filename,'w')

# Create two threads as follows
try:
 c=threading.Thread( target=client, args=(destIP,dport,) )
 s=threading.Thread( target=server, args=(sport,) )
 p=threading.Thread( target=ping, args=() )
 t=threading.Thread(target=timer,args=() )
except (KeyboardInterrupt,SystemExit):
   info("Error: unable to start thread")
   log.close()
   sys.exit()

t.start()
s.start()
time.sleep(1)
c.start()
#p.start()

