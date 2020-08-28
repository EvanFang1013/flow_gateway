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
logging.basicConfig(level=logging.INFO,
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
        # serial port and baudrate
        self._uport = uport
        self._ubd = ubd
        self.ser =serial.Serial(self._uport,baudrate = self._ubd)
        self.ser.timeout = 0.5
        logging.info('serial port open')
        # gpio id
        gp1 = 18;gp2 =23 ;gp3= 24;gp4=25;
        #gpio mapping MCU1<->18 /MCU2<->23  /MCU3<->24  /MCU4<->25 
        self.gpiolist=[gp1,gp2,gp3,gp4]
        GPIO.setmode(GPIO.BCM)
        # initial GPIO as LOW
        for io in self.gpiolist :
            GPIO.setup(io,GPIO.OUT,initial = GPIO.LOW)
        

    def modbus(self,svid):
        try:           
            #server = modbus_tcp.TcpServer(address=_localip,port=_port)
            self.server = modbus_tcp.TcpServer()                  
            self.server.start()
            logging.info("Modbus server start")
            self.slave = self.server.add_slave(svid)
            self.slave.add_block('ro', cst.HOLDING_REGISTERS, 0, 8)
            
        except: 
            logging.warning("Modbus server fail")
            self.server.stop()
            self.server._do_exit()
        
    def daq(self):
        try:
            # initial MCU miss data count
            for i in range(len(self.gpiolist)):locals()["M%scnt"%(i+1)] = 0
            while True:
                for i in range(len(self.gpiolist)):
                    GPIO.output(self.gpiolist[i],GPIO.HIGH)
                    if self.ser.isOpen():
                        try:
                            receive = self.ser.readline().decode()
                            print(receive)
                            title,data = receive.split(',')
                            self.slave.set_values('ro',i,int(data))
                            locals()["M%scnt"%(i+1)] = 0
                            GPIO.output(self.gpiolist[i],GPIO.LOW)
                        except:
                            locals()["M%scnt"%(i+1)] += 1
                            # ~ logging.info("MCU%s miss data Count = %s"%(i+1,locals()["M%scnt"%(i+1)]))
                            GPIO.output(self.gpiolist[i],GPIO.LOW)
                            if locals()["M%scnt"%(i+1)]>=3:
                                self.slave.set_values('ro',i,9999)
                                logging.warning("MCU%s miss data "%(i+1))
                                locals()["M%scnt"%(i+1)]=3
                            pass
                    time.sleep(0.01)
                time.sleep(0.5)
                    
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


    
    
