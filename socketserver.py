#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import socket
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
import time
import serial
import threading
import modbus_tk.modbus_tcp as modbus_tcp
import modbus_tk.defines as cst



class gateway():
    def __init__(self,sip,sport,uport,ubd):
        # gpio id
        self.gp1 = 18;self.gp2 =23 ;self.gp3= 24;
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gp1,GPIO.OUT,initial = GPIO.LOW)
        GPIO.setup(self.gp2,GPIO.OUT,initial = GPIO.LOW)
        GPIO.setup(self.gp3,GPIO.OUT,initial = GPIO.LOW)
        self._sip = sip
        self._sport = sport
        self._uport = uport
        self._ubd = ubd
        self.ser =serial.Serial(self._uport,baudrate = self._ubd)
        # ~ self.ser.timeout = 0.5
        
    def socket_listen(self):
        ack = False
        dis_count = 0
        server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.bind((self._sip,self._sport))
        server.listen(5)
        while True:
            conn,addr = server.accept() 
            print(conn,addr)
            while True:
                data = conn.recv(1024) 
                data = data.decode()
                if data:
                    arm,signal = data.split(',')
                    if (signal=='RunStart' and ack==False):
                        
                        GPIO.output(self.gp1,GPIO.HIGH)
                        ack = self.check()
                        conn.send("STOK".encode())
                        time.sleep(0.001)
                    if (signal=='RunEnd' and ack ==True):
                        t1 = time.time()
                        conn.send("END".encode())
                        GPIO.output(self.gp2,GPIO.HIGH)
                        self.daq()
                        print("########",time.time()-t1)
                        time.sleep(0.001)
                        ack = False
                        print("OK")
                        
                    GPIO.output(self.gp1,GPIO.LOW)
                    GPIO.output(self.gp2,GPIO.LOW)
                else:
                    break
            dis_count +=1   
            conn.close()
        
    def modbus(self,svid):
        try:           
            #server = modbus_tcp.TcpServer(address=_localip,port=_port)
            self.server = modbus_tcp.TcpServer()                  
            self.server.start()
            print ('server start..')
            self.slave = self.server.add_slave(svid)
            self.slave.add_block('ro', cst.HOLDING_REGISTERS, 0, 8)
            
        except: 
            print('server create fail')
            self.server.stop()
            self.server._do_exit()

    def check(self):
        receive1 = self.ser.readline().decode()
        print(receive1)
        if len(receive1)!=0:
            title1,data1 = receive1.split(',')
            if str(data1) =='Start_ACK\r\n':
                return True
            else: return False

                
    def daq(self):
        while True:
            receive = self.ser.readline().decode()
            title,data = receive.split(',')
            if title == 'gp18':
                self.slave.set_values('ro',0,int(data)%65535)
                print(int(data))
            if title == 'gp23':
                self.slave.set_values('ro',1,int(data)%65535)
                print(int(data)%65535)
            if title == 'gp24':
                self.slave.set_values('ro',2,int(data)%65535)
                print(int(data)%65535) 
            break
                                
        # ~ except KeyboardInterrupt:
            # ~ if serial != None:
                # ~ serial.close()
            
if __name__ == "__main__":
    # socket parameter
    socketIp = 'localhost'
    socketPort = 88
    # uart parameter
    uartPort = "/dev/ttyUSB0"
    uartBaudrate = 115200
    # modbus parameter
    mip = 'localhost' 
    svid = 1    
    
    g = gateway(socketIp,socketPort,uartPort,uartBaudrate)
    # ~ ut = threading.Thread(target = g.uart_listen)
    # ~ ut.start()
    g.modbus(svid)
    g.socket_listen()

    
    
