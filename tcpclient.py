#!/usr/bin/python

import sys
import socket
import time

i=0;
clientsocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', 8089))

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
clientsocket = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM)

