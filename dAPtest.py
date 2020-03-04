import decArrayProd as dap  # This contains the functions for creating the correct decimal array for printing
import shift as sr  # This contains the functions for shifting decimals into the shift register
import time  # Used for various purposes
from datetime import datetime
# import RPi.GPIO as GPIO  # Used to control RPi GPIO pins
import logging  # Used to log various operations and data

with open('PrinterLog.log', 'w'): pass
logging.basicConfig(filename='PrinterLog.log', format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
logging.info("Program start")


def log_command(ident, txt, lin, direct, dist):
    logging.info("Command ID: " + ident)
    logging.info("Text: " + txt)
    logging.info("Line type: " + str(lin))
    logging.info("Direction: " + direct)
    logging.info("Distance: " + str(dist))


droplets = 1
push = 0.0025  # time for push in seconds
pull = 0.0068  # time for pull in seconds
speed = 0.46  # time between print_jobs

# Establish TCP/IP connection with rover now
# Send handshakes now
# Begin sending/receiving Heartbeat now (including parsing incoming and updating status variables)
# Wake up Arduino and send message to prime, wait for response
# Establish second port for commands (handshake again?), then update status to ready to print
# On second port start listening for commands and deal with them as necessary like below
#

# -----------------------COMMAND INFORMATION-----------------------REMOVE LATER, BEFORE FINAL
identity = "36"
phrase = "12% 7p{}@#R"  # input('Phrase to print: ')
line = 4  # int(input('Line to print: '))
direction = "n"  # input('Direction: ')
distance = 0  # 14.8167mm
# -----------------------------------------------------------------
log_command(identity, phrase, line, direction, str(distance))


# wait for new command
# when command in: send message to rover to say "Preparing to print"
# Parse xml and assign variables to print data
[job, gap] = dap.create_array(phrase, line, direction, distance)  # decimal array produced using info from rover command
print(job)  # uncomment to print decimal array to screen

delay = gap / (speed*1000)

trigger = 0
# send message to rover to say "Ready to print"
while trigger == 0:  # wait for trigger from rover to start printing
    trigger = int(input('Trigger? '))  # replace with function to check trigger

for x in range(len(job)):
    sr.shift_in(job[x])
    # sr.print_job(droplets, push, pull)
    time.sleep(delay)  # check status till correct distance has been reached (14.82 mm)
    logging.info("Column " + str(x+1) + "/" + str(len(job)) + " printed.")

logging.info("Command ID=" + identity + " printed.")
trigger = 0   # reset trigger
# send message to Rover to say "Print complete"
