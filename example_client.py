#!/usr/bin/python

import socket
import select
import sys
import time
from threading import Thread
import xml.etree.ElementTree as ET
from rospkg import RosPack
import itertools as IT
import random as rnd
import io
StringIO = io.BytesIO

""" Setting up a client to TCP/IP comm testing """

Server_IP = "10.0.0.17"
# Server_IP = "10.27.11.2"
# Server_IP = "172.20.10.12"
Server_Port = 22171

command = "<?xml version='1.0' encoding='UTF-8'?><Rugged><Command><ID>12</ID><Text>Rugged</Text><Lines>4</Lines><Direction>270</Direction><Distance>400</Distance><Begin>1</Begin></Command></Rugged>"
heartbeat = "<Rugged><Status><Activity>ACTIVE</Activity><Errors>0</Errors><RoverSpeed>0.5</RoverSpeed><Distance>1</Distance></Status></Rugged>"
handshake = "<?xml version='1.0' encoding='UTF-8'?><Rugged><Handshake><Functional>YES</Functional></Handshake></Rugged>"
trigger = "<?xml version='1.0' encoding='UTF-8'?><Rugged><Trigger><StartPrinting>GO</StartPrinting></Trigger></Rugged>"



class TestClient(object):
    """ Setup the basics of the client """

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # This populates with the the IP and port, lookup what port to use.
        # ex: self.server_address = ("192.168.1.100", 22171)
        self.server_address = (Server_IP, Server_Port)

    """ Connect and talk at an interval to the server """

    def send(self, message):
        try:
            self.sock.sendall(message.encode("ASCII"))
            print("Message sent: {}".format(message))
        except:
            print("Error: sending failed")

    def run(self):

        # connect to the the server
        print("[Rover]: Connecting to %s on port %s as client" % self.server_address)
        while True:
            try:
                self.sock.connect(self.server_address)
                break
            except:
                pass
        # startup thread to read any messages back from the server
        self._data_thread = Thread(target=self._run_data_thread)
        self._data_thread.daemon = True   # makes the thread dependant on the parent program, so they die together
        self._data_thread.start()

        # self.sock.sendall(handshake.encode("ASCII"))
        # print("Message sent: {}".format(handshake))
        # send a message with a certain frequency a certain number of times
        global HS
        global primed
        global printing
        global Activity
        global purged
        HS = 0
        primed = 0
        printing = 0
        while not HS:  # wait for handshake from printer (server)
            continue

        time.sleep(1)
        TestClient.send(self, handshake)
        time.sleep(1)

        hb = Thread(target=self.sendHB)
        hb.daemon = True
        hb.start()

        while not primed:
            continue

        comms = 0
        while comms < 4:
            if primed and not purged:
                command = "<?xml version='1.0' encoding='UTF-8'?><Rugged><Command><ID>" + str(comms+1) + "</ID><Text>Rugged</Text><Lines>4</Lines><Direction>270</Direction><Distance>40</Distance><Begin>1</Begin></Command></Rugged>"
                TestClient.send(self, command)
                time.sleep(0.1)
                # input("Trigger? ")
                TestClient.send(self, trigger)
                time.sleep(1)
            while printing:
                continue
            comms += 1
        Activity = "INACTIVE"

        while not purged:
            continue

        print("[Rover]: Closing socket")
        self.sock.close()
        quit()


    def _run_data_thread(self):
        print("data thread starting")
        global HS
        global primed
        global printing
        global purged
        purged = 0
        while True:
            data = ''
            # check for data on the buffer
            ready = select.select([self.sock], [], [], 0.01)
            # if data on the buffer, read it
            if ready[0]:
                data = self.sock.recv(1024)
            if data:
                # print('Message received: %s' % data.decode("ASCII"))
                if data.decode("ASCII") == "<?xml version='1.0' encoding='UTF-8'?><Blueprint><Handshake><Functional>YES</Functional><Functional>NO</Functional></Handshake></Blueprint>":
                    HS = 1
                elif data.decode("ASCII") == "<Blueprint><Status><Activity>Ready</Activity><Errors>0</Errors></Status></Blueprint>":
                    primed = 1
                    printing = 0
                elif data.decode("ASCII") == "<Blueprint><Status><Activity>Printing</Activity><Errors>0</Errors></Status></Blueprint>":
                    printing = 1
                elif data.decode("ASCII") == "<Blueprint><Status><Activity>Purged</Activity><Errors>0</Errors></Status></Blueprint>":
                    printing = 0
                    purged = 1
            else:
                pass
            time.sleep(0.01)

    def sendHB(self):
        global Activity
        Activity = "ACTIVE"
        while True:
            message = "<?xml version='1.0' encoding='UTF-8'?><Rugged><Status><Activity>" + Activity + "</Activity><Errors>0</Errors><RoverSpeed>" + str(
            rnd.randint(40, 50)) + "</RoverSpeed><Distance>1</Distance></Status></Rugged>"
            try:
                self.sock.sendall(message.encode("ASCII"))
            except:
                print("Error: sending failed")
                break
            time.sleep(0.05)



if __name__ == "__main__":
    global HS
    global printing
    client = TestClient()
    client.run()

