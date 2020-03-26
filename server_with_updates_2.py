#!/usr/bin/python3
import socket
import select
import sys
import time
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring, Element, SubElement
#from rospkg import RosPack
from threading import Thread, Lock
from copy import deepcopy
from datetime import datetime
import parseFromString1 as pfs
import logging
import decArrayProd as dap
import shift as sr
import serial
# from xmlToVari import xml2vari as xml2v
logname = datetime.now().strftime("%Y-%m-%d")
with open(logname + '_PrinterLog.log', 'w'):pass
logging.basicConfig(filename=logname + '_PrinterLog.log', format='%(asctime)s - %(levelname)s: %(message)s',level=logging.INFO) # 
logging.info("Program start")

"""Setting up Arduino USB serial port"""
ard = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)

def sendToArd(signal):
    ard.write(signal.encode())
    if signal == "1":
        print("[Printer]: Prime sequence initiated")
        logging.info("Prime sequence initiated")
    elif signal == "2":
        print("[Printer]: Purge sequence initiated")
        logging.info("Purge sequence initiated")

def readArd():
    ret = ard.read().decode("ASCII")#line()#.decode()
    return ret

def prime():
    global printerActivity
    sendToArd("1")
    while ard.inWaiting() < 1:
        continue
    retu = readArd()
    while retu == "1":
        printerActivity = "Priming"
        print("Priming...")
        logging.info("System priming...")
        while ard.inWaiting() < 1:
            continue
        retu = readArd()
    if retu == "2":
        print("Primed")
        logging.info("System primed and ready")
        printerActivity = "Ready"

def purge():
    global printerActivity
    sendToArd("2")
    while ard.inWaiting() < 1:
        continue
    retu = readArd()
    while retu == "3":
        printerActivity = "Purging"
        print("Purging...")
        logging.info("System purging...")
        while ard.inWaiting() < 1:
            continue
        retu = readArd()
    if retu == "4":
        print("Purged")
        logging.info("System purged")
        printerActivity = "Purged"

""" Setting up a server to TCP/IP comm testing """

Server_IP = "10.0.0.17"  # home
# Server_IP = "10.27.11.2"  # school
# Server_IP = "172.20.10.12" # my iPhone hotspot
Server_Port = 22171

handshake = b"<?xml version='1.0' encoding='UTF-8'?><Blueprint><Handshake><Functional>YES</Functional><Functional>NO</Functional></Handshake></Blueprint>"

class xml2vari():
    
    def __init__(self):
        global Text
        global Lines
        global Direction
        global Length
        global Activity
        global Errors
        global RoverSpeed
        global Distance
        global Functional
        global Start
        global printerActivity
        global printerErrors
        Text = None
        Lines = None
        Direction = None
        Length = None
        Activity = None
        Errors = None
        RoverSpeed = None
        Distance = None
        Functional = None
        Start = None


    def parseCmd(message):
        
        global ID
        global Text  # update to match stucture set by Rugged Robotics**
        global Lines
        global Direction
        global Length
        global Begin
        global job
        global gap
        global printerActivity
        printerActivity = "Processing"
        
        contents = message.findall(".//")
        ID = contents[1].text
        Text = contents[2].text
        Lines = contents[3].text
        Direction = contents[4].text
        Length = contents[5].text
        Begin = contents[6].text
        
        logging.info("Command ID: " + ID)
        logging.info("Text: " + Text)
        logging.info("Lines: " + Lines)
        logging.info("Direction: " + Direction)
        logging.info("Distance: " + Length)
        logging.info("Begin: " + Begin)
        
        [job, gap] = dap.create_array(Text, int(Lines), Direction, int(Length))
#         print(job)
        Text = None
        Lines = None
        Direction = None
        Length = None
        printerActivity = "Ready"
#         time.sleep(0.003)
#         params = (Text, Lines, Direction, Length)
#         return params

    def parseStat(message):
        
        global Activity  # update to match stucture set by Rugged Robotics**
        global Errors
        global RoverSpeed
        global Distance
        
        contents = message.findall(".//")
        Activity = contents[1].text
        Errors = contents[2].text
        RoverSpeed = contents[3].text
        Distance = contents[4].text
        
#         try:
#             logging.info("Activity: " + Activity)
#             logging.info("Errors: " + Errors)
#             logging.info("Speed: " + RoverSpeed)
#             logging.info("Distance: " + Distance)
#         except TypeError:
#             pass
#         params = (Activity, Errors, RoverSpeed, Distance)
#         return params

    def parseHS(message):
        
        global Functional  # update to match stucture set by Rugged Robotics**
        global primed
        global printerActivity
        contents = message.findall(".//")
        Functional = contents[1].text
        print("[Printer]: Handshake received, Functional: ", Functional)
        logging.info("Functional: " + Functional)
        if Functional == "YES":
#             prime()
#             primed = 1
            prime_thread = Thread(target=prime)
            prime_thread.daemon = True
            prime_thread.start()
            primed = 1
#             sendToArd("1")#*********************************************************HERE
#         while ard.inWaiting() < 1:
#             continue
#         retu = readArd()
#         while retu == "1":
#             printerActivity = "Priming"
#             print("Priming...")
#             logging.info("System priming...")
#             while ard.inWaiting() < 1:
#                 continue
#             retu = readArd()
#         if retu == "2":
#             print("Primed")
#             logging.info("System primed and ready")
#             printerActivity = "Ready"
            
        
    def parseTrig(message):
        
        global Start  # update to match stucture set by Rugged Robotics**
        
        contents = message.findall(".//")
        Start = contents[1].text
        logging.info("Start: " + Start)
        params = (Start)
        return params

    def checkMessage(message):
        for elem in message:
            if elem.tag == "Command":
                params = xml2vari.parseCmd(message)
                logging.info("Command ID: " + ID + " ready to print.")
            elif elem.tag == "Status":
                params = xml2vari.parseStat(message)
            elif elem.tag == "Handshake":
#                 params = xml2vari.parseHS(message)
                xml2vari.parseHS(message)
            elif elem.tag == "Trigger":
                params = xml2vari.parseTrig(message)
            else:
                break
#         return params

    def parseMessage(self, comms):
        global printerErrors
        
        strcomm = comms.decode("ASCII")
        try:
            message = ET.XML(comms)
            params = xml2vari.checkMessage(message)
            return params
        except:
            printerErrors = "1"
            print("Parsing error")
            logging.error("Parsing error: " + str(comms))
            pass
#         params = xml2vari.checkMessage(message)
#         return params
def sendHB():
    global printerActivity
    global printerErrors
    printerActivity = "Starting up"
    printerErrors = "0"
#     global printerAvailability
    Blueprint = Element('Blueprint')
    Status = SubElement(Blueprint, 'Status')
    activity = SubElement(Status, 'Activity')
    errors = SubElement(Status, 'Errors')
    while True:
        activity.text = printerActivity
        errors.text = printerErrors
        printerHB = tostring(Blueprint)
        server.connection.sendall(printerHB)
#         print(printerActivity)
        printerErrors = "0"
#         print("printerHB sent")
#         print(printerHB)
        time.sleep(0.03)
    
class TestServer(object):
    """ Setup the basics of the server """

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (Server_IP, Server_Port)
        self._lock = Lock()
        self._data = []

    """ Start the server comm on localhost """

    def run(self):
        print("[Printer]: Starting as server at %s with port %s" % self.server_address)
        logging.info("Starting as server at %s with port %s" % self.server_address)
        # set to reconnect to avoid timeout issues
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server_address)
        self.connected = False
        self.sock.listen(1)

        while not self.connected:
            print('[Printer]: Waiting for connection...')
            self.connection, self.client_address = self.sock.accept()
            time.sleep(0.5)
            if self.connection:
                self.connected = True

        print("[Printer]: New client at %s with port %s" % self.client_address)
        logging.info("New client at %s with port %s" % self.client_address)

#         spin up reading thread
        self._data_thread = Thread(target=self._run_data_thread)
        self._data_thread.daemon = True
        self._data_thread.start()
        input("Send HS: ")##############################################################
        self.connection.sendall(handshake)
        print("[Printer]: Handshake sent to client at %s with port %s" % self.client_address)
        logging.info("Handshake sent to client at %s with port %s" % self.client_address)
        
        while self.connected:
#             set the lock to read the current common variable lock will release with with statement ends
            with self._lock:
                if self._data:
#                     print("Current data in buffer is {}".format(self._data))
                    message = self._data.pop(0)
                    ser.parseMessage(message)
                else:
                    pass
#           time.sleep(0.5)

    def _run_data_thread(self):
        print("[Printer]: Data thread starting")
        while self.connected:
            data = ''
#             check for data on the buffer
            ready = select.select([self.connection], [], [], 0.5)
#             if data on the buffer, read it
            if ready[0]:
                data = self.connection.recv(1024)
            if data:
#                 print('Data received: %s' % data)#.decode("ASCII"))
#                 return a copy to the user of what they sent
#                 self.connection.sendall(deepcopy(data))
#                 set the lock to manipulate the common variable
#                 when the with section ends, the lock is released
                with self._lock:
                    self._data.append(data)
#                     print(self._data)
                data = ''
            else:
                pass
#             time.sleep(0.005)#*****************************************************************

def printing():
    global ID
    global Text
    global Lines
    global Direction
    global Length
    global Begin
    global Start
    global Activity
    global Errors
    global RoverSpeed
    global Distance
    global Functional
    global Start
    global job
    global gap
    global Availability
    global printerActivity
    global printerErrors
    global primed
    job = 0
    Start = 0
#     printerActivity = 0#"Waiting"
    primed = 0
    printerErrors = "0"
    printerActivity = "Priming"
    while Activity == None:
        continue
    while Functional == "YES" and Activity == "ACTIVE":# and primed == 1:
#         printerActivity = "Ready"
#         Tell Arduino to Prime
#         print(Activity, Errors, RoverSpeed, Distance)
#         print(Text, Lines, Direction, Length)
        if job and Start:
            for x in range(int(Begin)-1, len(job)):
                if Activity == "ACTIVE" and Errors == "0":
                    printerActivity = "Printing"
                    sr.shift_in(job[x])
#                 sr.print_job()
                    logging.info("ID: " + ID + "; Element " + str(x+1) + "/" + str(len(job)) + " printed")
                    delay = int(gap)/float(RoverSpeed) #* int(gap)
#                     print(RoverSpeed, round(delay))
                    time.sleep(delay)
                else:
                    logging.info("Status is inactive, waiting...")
                    printerActivity = "Waiting"
                    while Activity != "ACTIVE":
                        continue
            job = None
            gap = None
            Start = 0
            printerActivity = "Ready"
#             Direction = None
#             Length = None
        time.sleep(0.03)
#         print(Activity)
    if Activity == "INACTIVE":
        purge()
        logging.info("Printing thread closing")
        quit()

if __name__ == "__main__":
    global job
    global printerActivity
    global printerErrors
    server = TestServer()
    ser = xml2vari()
    comm_thread = Thread(target=server.run)
    comm_thread.daemon = True
    comm_thread.start()
    while not Functional:  # waiting for handshake to say functional
        continue
#     time.sleep(1)
    status_thread = Thread(target=sendHB)
    status_thread.daemon = True
    status_thread.start()
    
    print_thread = Thread(target=printing)
    print_thread.daemon = True
    print_thread.start()
    
    print_thread.join()
    comm_thread.join()
    status_thread.join()
    
    quit()
#     printing()

  
  
