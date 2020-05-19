#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import socket
import RPi.GPIO as GPIO
import datetime
GPIO.setwarnings(False)
import time
import serial
import threading
import modbus_tk.modbus_tcp as modbus_tcp
import modbus_tk.defines as cst
import logging
from logging.handlers import TimedRotatingFileHandler

log_filename = datetime.datetime.now().strftime("./log/%Y-%m-%d_%H_%M.log")
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    handlers = [TimedRotatingFileHandler(filename =log_filename ,when="D",interval=1,backupCount=30)]
                    )
#TimedRotatingFileHandler ()
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console) 

class gateway():
    def __init__(self,uport,ubd):
        # gpio id
        self._uport = uport
        self._ubd = ubd
        self.ser =serial.Serial(self._uport,baudrate = self._ubd)
        logging.info('serial port open')
        

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
        
    def daq(self):
        try:
            while True:
                if self.ser.isOpen():
                    receive = self.ser.readline().decode()
                    title,data = receive.split(',')
                    if title == 'MCU1':
                        self.slave.set_values('ro',0,int(data))
                        print(int(data))
                    if title == 'MCU2':
                        self.slave.set_values('ro',1,int(data))
                        print(int(data))
                    if title == 'MCU3':
                        self.slave.set_values('ro',2,int(data))
                        print(int(data))
                    if title == 'MCU4':
                        self.slave.set_values('ro',3,int(data))
                        print(int(data))
        except:
            self.slave.set_values('ro',4,9999)
            logging.warning('Serial port Close.')
            
               

            
if __name__ == "__main__":
  
    uartPort = "/dev/ttyUSB0"
    uartBaudrate = 115200
    # modbus parameter
    mip = 'localhost' 
    svid = 1    
    
    g = gateway(uartPort,uartBaudrate)
    g.modbus(svid)
    g.daq()


    
    
