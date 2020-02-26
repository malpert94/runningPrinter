import decArrayProd as dap
import shift as sr
import time
from datetime import datetime
# import RPi.GPIO as GPIO


def date():
    d = datetime.now()
    return d


date()


droplets = 3
push = 0.0025  # time for push in seconds
pull = 0.0068  # time for pull in seconds
delay = 0.5  # time between print_jobs


# -----------------------COMMAND INFORMATION-----------------------
phrase = "i"  # input('Phrase to print: ')
line = 4  # int(input('Line to print: '))
direction = "N"  # input('Direction: ')
distance = 30  # 14.8167mm
# -----------------------------------------------------------------

# wait for new command
# when command in: send message to rover to say "Preparing to print"
# Parse xml and assign variables to print data

job = dap.create_array(phrase, line, direction, distance)  # decimal array produced using info from command from rover
# print(job)  # uncomment to print decimal array to screen

trigger = 0
# send message to rover to say "Ready to print"
while trigger == 0:  # wait for trigger from rover to start printing
    trigger = int(input('Trigger? '))  # replace with function to check trigger

for x in range(len(job)):
    sr.shift_in(job[x])
    sr.print_job(droplets, push, pull)
    time.sleep(delay)  # check status till correct distance has been reached (14.82 mm)

trigger = 0   # reset trigger
# send message to Rover to say "Print complete"
