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
import parseFromString1 as pfs  # used to parse information from incoming XML
import logging
import decArrayProd as dap  # used to convert incoming commands into decimal array 
import shift as sr  # used to print 
import serial  # used to communicate with the Arduino
# from xmlToVari import xml2vari as xml2v

logname = datetime.now().strftime("%Y-%m-%d") + '_PrinterLog.log'  # log name based off of date
with open(logname, 'w'):pass
logging.basicConfig(filename=logname, format='%(asctime)s - %(levelname)s: %(message)s',level=logging.INFO) # 
logging.info("Program start")  # logging the start of the program

ard = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)  # Setting up Arduino USB serial port

def sendToArd(signal):  # function to send prime or purge message to Arduino
    ard.write(signal.encode())
    if signal == "1":
        print("[Printer]: Prime sequence initiated")
        logging.info("Prime sequence initiated")
    elif signal == "2":
        print("[Printer]: Purge sequence initiated")
        logging.info("Purge sequence initiated")

def readArd():  # function to read and decode messages from Arduino
    ret = ard.read().decode("ASCII")#line()#.decode()
    return ret

def prime():  # function to prime system
    global printerActivity
    sendToArd("1")  # send a "1" to tell Arduino to prime
    while ard.inWaiting() < 1:  # wait for response
        continue
    retu = readArd()  # read response
    while retu == "1":
        printerActivity = "Priming"  # check to see if system is priming
        print("[Printer]: Priming...")
        logging.info("System priming...")
        while ard.inWaiting() < 1:  # wait for response
            continue
        retu = readArd()
    if retu == "2":  # check to see if system is primed
        print("[Printer]: Primed")
        logging.info("System primed and ready")
        printerActivity = "Ready"  # printer ready to start printing

def purge():  # function to purge system
    global printerActivity
    sendToArd("2")  # send a "2" to tell Arduino to purge
    while ard.inWaiting() < 1:  # wait for response
        continue
    retu = readArd()  # read response
    while retu == "3":
        printerActivity = "Purging" # check to see if system is purging
        print("[Printer]: Purging...")
        logging.info("System purging...")
        while ard.inWaiting() < 1:  # wait for response
            continue
        retu = readArd()
    if retu == "4":  # check to see if system is purged
        print("[Printer]: Purged")
        logging.info("System purged")
        printerActivity = "Purged"
        

""" Setting up a server to TCP/IP comm testing """

# Server_IP = "10.27.11.2"  # school
# Server_IP = "172.20.10.12" # my iPhone hotspot
Server_IP = "10.0.0.17"  # home
Server_Port = 22171

handshake = b"<?xml version='1.0' encoding='UTF-8'?><Blueprint><Handshake><Functional>YES</Functional><Functional>NO</Functional></Handshake></Blueprint>"

class xml2vari():  # set of functions to handle incoming messages
    
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


    def parseCmd(message):  # function to parse a command and assign the informatin to variables
        
        global ID  # Command ID
        global Text  # Text to be printed
        global Lines  # Lines to be printed
        global Direction  # Direction for orientation
        global Length  # length of line(s) to be printed
        global Begin  # element number to start at (incase of previos error)
        global job  # decimal array (passed on to printing phase)
        global gap  # distance between dots (passed on to printing phase)
        global printerActivity  # current status of printer
        printerActivity = "Processing"  # set status to processing so no other commands are sent
        
        contents = message.findall(".//")  # create array of information in command than assign each element to a variable
        ID = contents[1].text 
        Text = contents[2].text
        Lines = contents[3].text
        Direction = contents[4].text
        Length = contents[5].text
        Begin = contents[6].text
        
        logging.info("Command ID: " + ID)  # log the new command information
        logging.info("Text: " + Text)
        logging.info("Lines: " + Lines)
        logging.info("Direction: " + Direction)
        logging.info("Distance: " + Length)
        logging.info("Begin: " + Begin)
        
        [job, gap] = dap.create_array(Text, int(Lines), Direction, int(Length))  # use the variables to create a decimal array for printing
#         print(job)
        Text = None  # clear out the variables
        Lines = None
        Direction = None
        Length = None
        logging.info("Command ID: " + ID + " ready to print.")
        printerActivity = "Ready"  # set status to ready ro print
#         time.sleep(0.003)

    def parseStat(message):  # function to parse info from status updates from rover
        
        global Activity  # is the printer to be active?
        global Errors  # any errors
        global RoverSpeed  # speed of rover for printing timing
        global Distance  # might not need at the moment
        
        contents = message.findall(".//")  # create array of information in command than assign each element to a variable
        Activity = contents[1].text
        Errors = contents[2].text
        RoverSpeed = contents[3].text
        Distance = contents[4].text


    def parseHS(message):  # function to parse info in Handshake response
        
        global Functional  # Will the printer be in use? (YES or NO)
        global primed
        global printerActivity
        contents = message.findall(".//")  # create array of inormation in handshake 
        Functional = contents[1].text  # assign to variable
        print("[Printer]: Handshake received, Functional: ", Functional)
        logging.info("Functional: " + Functional)  # logg Handshake response
        if Functional == "YES":  # if the printer is to be used start the priming thread
#             prime()
#             primed = 1
            prime_thread = Thread(target=prime)
            prime_thread.daemon = True
            prime_thread.start()
            primed = 1
        else:
            sys.exit()  # if printer not to be used shutdown
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
            
        
    def parseTrig(message):  # function to parse trigger
        
        global Start  # trigger variable
        
        contents = message.findall(".//")  # create array of inormation in handshake 
        Start = contents[1].text  # assign info to variable
        logging.info("Start: " + Start)


def checkMessage(message):  # function to determine which type of message is to be parsed
    for elem in message:
        if elem.tag == "Command":
            xml2vari.parseCmd(message)                
        elif elem.tag == "Status":
            xml2vari.parseStat(message)
        elif elem.tag == "Handshake":
            xml2vari.parseHS(message)
        elif elem.tag == "Trigger":
            xml2vari.parseTrig(message)
        else:
            break

def parseMessage(comms):
    try:
        message = ET.XML(comms)
        checkMessage(message)
    except:
#         global printerErrors
#         printerErrors = "1"
#         print("Parsing error")
#         logging.error("Parsing error: " + str(comms))
        decod = comms.decode("ASCII")
        ender = "</Rugged>"
        comd = "<Command>"
        trigg = "<Trigger>"
        recovered = []
        n = decod.count(ender)
        for x in range(n):
            t = decod.partition(ender)[0] + decod.partition(ender)[1]
            decod = decod.partition(ender)[2]
            if comd in t:
                recovered.append(t)
            elif trigg in t:
                recovered.append(t)
            elif x == n-1:
                recovered.append(t)
        for s in recovered:
            message = ET.XML(s)
            checkMessage(message)


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
        try:
            server.connection.sendall(printerHB)
        except:
            break
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
        self.connection.sendall(handshake)
        print("[Printer]: Handshake sent to client at %s with port %s" % self.client_address)
        logging.info("Handshake sent to client at %s with port %s" % self.client_address)
        
        while self.connected:
#             set the lock to read the current common variable lock will release with with statement ends
            with self._lock:
                if self._data:
#                     print("Current data in buffer is {}".format(self._data))
                    message = self._data.pop(0)
#                     ser.
                    parseMessage(message)
                else:
                    pass
#           time.sleep(0.5)

    def _run_data_thread(self):
        print("[Printer]: Data thread starting")
        while self.connected:
            data = ''
#             check for data on the buffer
            ready = select.select([self.connection], [], [], 0.5)######################
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
    primed = 0
    printerErrors = "0"
    printerActivity = "Priming"
    while Activity == None:
        continue
    while Functional == "YES" and Activity == "ACTIVE":# and primed == 1:
#         printerActivity = "Ready"
        if job and Start:
            for x in range(int(Begin)-1, len(job)):
                if Activity == "ACTIVE" and Errors == "0":
                    printerActivity = "Printing"
                    sr.shift_in(job[x])
                    sr.print_job()
                    logging.info("ID: " + ID + "; Element " + str(x+1) + "/" + str(len(job)) + " printed")
                    delay = int(gap)/float(RoverSpeed)
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
        time.sleep(0.03)
        
    if Activity == "INACTIVE":
        purge()
        logging.info("Printing thread closing")
#         os.system("sudo shutdown -h now")
        sys.exit()

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
    print("Printing thread closing")
    sys.exit()
    comm_thread.join()
    print("comm thread closing")
    status_thread.join()
    

  
  
