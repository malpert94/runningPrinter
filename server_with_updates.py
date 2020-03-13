#!/usr/bin/python

import socket
import select
import sys
import time
import xml.etree.ElementTree as ET
#from rospkg import RosPack
from threading import Thread, Lock
from copy import deepcopy
import parseFromString1 as pfs
import logging
import decArrayProd as dap
import shift as sr
# from xmlToVari import xml2vari as xml2v
with open('PrinterLog.log', 'w'):pass
logging.basicConfig(filename='PrinterLog.log', format='%(asctime)s - %(levelname)s: %(message)s',level=logging.INFO) #
logging.info("Program start")
""" Setting up a server to TCP/IP comm testing """

Server_IP = "10.0.0.18"  # home
# Server_IP = "10.27.11.2"
Server_Port = 22171

handshake = b'<Blueprint><Handshake><Functional>YES</Functional><Functional>NO</Functional></Handshake></Blueprint>'

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
                
        global Text  # update to match stucture set by Rugged Robotics**
        global Lines
        global Direction
        global Length
        global job
        global gap
        
        contents = message.findall(".//")
        Text = contents[1].text
        Lines = contents[2].text
        Direction = contents[3].text
        Length = contents[4].text
        
        logging.info("Text: " + Text)
        logging.info("Lines: " + Lines)
        logging.info("Direction: " + Direction)
        logging.info("Distance: " + Length)
        
        [job, gap] = dap.create_array(Text, int(Lines), Direction, int(Length))
        
        Text = None
        Lines = None
        Direction = None
        Length = None
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
        
        try:
            logging.info("Activity: " + Activity)
            logging.info("Errors: " + Errors)
            logging.info("Speed: " + RoverSpeed)
            logging.info("Distance: " + Distance)
        except TypeError:
            pass
        params = (Activity, Errors, RoverSpeed, Distance)
        return params

    def parseHS(message):
        
        global Functional  # update to match stucture set by Rugged Robotics**
        
        contents = message.findall(".//")
        Functional = contents[1].text
        logging.info("Functional: " + Functional)
        
        params = (Functional)
        return params
        
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
            elif elem.tag == "Status":
                params = xml2vari.parseStat(message)
            elif elem.tag == "Handshake":
                params = xml2vari.parseHS(message)
            elif elem.tag == "Trigger":
                params = xml2vari.parseTrig(message)
            else:
                break
        return params

    def parseMessage(self, comms):
        strcomm = comms.decode("ASCII")
        message = ET.XML(comms)
        params = xml2vari.checkMessage(message)
        return params

# ser = xml2vari()
class TestServer(object):
  """ Setup the basics of the server """
  #global value

  def __init__(self):
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # This populates with the the IP and port, lookup what port to use.
    # ex: self.server_address = ("192.168.1.100", 22171)
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
      # wait for the connection
      print('[Printer]: Waiting for connection...')
      self.connection, self.client_address = self.sock.accept()
      time.sleep(0.5)
      if self.connection:
        self.connected = True

    print("[Printer]: New client at %s with port %s" % self.client_address)
    logging.info("New client at %s with port %s" % self.client_address)

    # spin up reading thread
    self._data_thread = Thread(target=self._run_data_thread)
    self._data_thread.daemon = True
    self._data_thread.start()
#     self.connection.sendall(handshake)
#     print("[Printer]: Handshake sent to client at %s with port %s" % self.client_address)
#     logging.info("Handshake sent to client at %s with port %s" % self.client_address)
    while self.connected:
      # set the lock to read the current common variable
      # lock will release with with statement ends
      with self._lock:
        if self._data:
#             print("Current data in buffer is {}".format(self._data))
            message = self._data.pop(0)
#             global Text
            ser.parseMessage(message)
#             print("Speed: ", RoverSpeed)
        else:
            pass
#       time.sleep(0.5)

  def _run_data_thread(self):
    print("Data thread starting")
    while self.connected:
      data = ''
      # check for data on the buffer
      ready = select.select([self.connection], [], [], 0.01)
      # if data on the buffer, read it
      if ready[0]:
        data = self.connection.recv(1024)
      if data:
#         print('Data received: %s' % data)#.decode("ASCII"))
        # return a copy to the user of what they sent
        self.connection.sendall(deepcopy(data))
        # set the lock to manipulate the common variable
        # when the with section ends, the lock is released
        with self._lock:
          self._data.append(data)#.decode("ASCII"))
        data = ''
      else:
        pass
      time.sleep(0.01)

def printing():
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
    global job
    global gap
    job = 0
    while Functional == "YES":
        # Tell Arduino to Prime
        print(Activity, Errors, RoverSpeed, Distance)
        if job:
            print(job)
            print(gap)
            begin = 1
            delay = 0.5
            for x in range(begin-1, len(job)):
                sr.shift_in(job[x])
#                 sr.print_job()
                time.sleep(delay)
            job = None
            gap = None
#             Direction = None
#             Length = None
        time.sleep(0.1)

if __name__ == "__main__":
    global job
    server = TestServer()
    ser = xml2vari()
    comm_thread = Thread(target=server.run)
    comm_thread.daemon = True
    comm_thread.start()
    time.sleep(3)
    comm_thread = Thread(target=printing)
    comm_thread.daemon = True
    comm_thread.start()
    
  
  
