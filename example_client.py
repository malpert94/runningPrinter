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

command = "<?xml version='1.0' encoding='UTF-8'?><Rugged><Command><ID>54</ID><Text>WALL</Text><Lines>4</Lines><Direction>90</Direction><Distance>250</Distance><Begin>1</Begin></Command></Rugged>"
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

    def run(self):

        # connect to the the server
        print("[Rover]: Connecting to %s on port %s as client" % self.server_address)
        self.sock.connect(self.server_address)

        # startup thread to read any messages back from the server
        self._data_thread = Thread(target=self._run_data_thread)
        self._data_thread.daemon = True   # makes the thread dependant on the parent program, so they die together
        self._data_thread.start()

        # self.sock.sendall(handshake.encode("ASCII"))
        # print("Message sent: {}".format(handshake))
        # send a message with a certain frequency a certain number of times
        global HS
        HS = 0
        while not HS:
            continue

        try:
            self.sock.sendall(handshake.encode("ASCII"))
            print("Message sent: {}".format(handshake))
        except:
            print("error while sending")
        time.sleep(1)
        for count in range(0,1):
            # send a message piece
            try:
                message = "<?xml version='1.0' encoding='UTF-8'?><Rugged><Status><Activity>ACTIVE</Activity><Errors>0</Errors><RoverSpeed>" + str(rnd.randint(10, 50)) + "</RoverSpeed><Distance>1</Distance></Status></Rugged>"
                #message = str(count)
                self.sock.sendall(message.encode("ASCII"))
                print("Message sent: {}".format(message))
            except:
                print("error while sending")
            time.sleep(0.033)
        try:
            self.sock.sendall(command.encode("ASCII"))
            print("Message sent: {}".format(command))
        except:
            print("error while sending")
        time.sleep(0.033)
        try:
            self.sock.sendall(trigger.encode("ASCII"))
            print("Message sent: {}".format(trigger))
        except:
            print("error while sending")
        time.sleep(0.033)
        while True:
            # send a message piece
            try:
                message = "<?xml version='1.0' encoding='UTF-8'?><Rugged><Status><Activity>ACTIVE</Activity><Errors>0</Errors><RoverSpeed>" + str(rnd.randint(30,70)) + "</RoverSpeed><Distance>1</Distance></Status></Rugged>"
                # message = str(count)
                self.sock.sendall(message.encode("ASCII"))
                print("Message sent: {}".format(message))
            except:
                print("error while sending")
                break
            time.sleep(0.033)



        print("[Rover]: Closing socket")
        self.sock.close()


    def _run_data_thread(self):
        print("data thread starting")
        global HS
        while True:
            data = ''
            # check for data on the buffer
            ready = select.select([self.sock], [], [], 0.01)
            # if data on the buffer, read it
            if ready[0]:
                data = self.sock.recv(1024)
            if data:
                print('Message received: %s' % data.decode("ASCII"))
                if data.decode("ASCII") == "<?xml version='1.0' encoding='UTF-8'?><Blueprint><Handshake><Functional>YES</Functional><Functional>NO</Functional></Handshake></Blueprint>":
                    HS = 1
                # ret = data
                # print("ret = ", ret)
                data = ''
            else:
                pass
            time.sleep(0.01)


if __name__ == "__main__":
    global HS
    client = TestClient()
    client.run()

