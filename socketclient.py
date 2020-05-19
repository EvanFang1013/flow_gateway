#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import socket
import time
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(('localhost',88))
while True:
    msg = 'A,RunStart'
    msg2 = 'A,RunEnd' 
    client.send(msg.encode('utf-8')) 
    data = client.recv(1024) 
    print('recv:',data.decode()) 
    time.sleep(1)
    client.send(msg2.encode('utf-8')) 
    data = client.recv(1024) 
    print('recv:',data.decode()) 
    time.sleep(5)

client.close() 
