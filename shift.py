# import RPi.GPIO as GPIO
import time

'''
dataPin = 6
OEPin = 13
latchPin = 19
clockPin = 26

droplets = 3
push = 0.0025  # time for push in seconds
pull = 0.0068  # time for pull in seconds

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(dataPin, GPIO.OUT)
GPIO.setup(OEPin, GPIO.OUT)
GPIO.setup(latchPin, GPIO.OUT)
GPIO.setup(clockPin, GPIO.OUT)
GPIO.output(OEPin, 1)


def pulsePin(pin):
    GPIO.output(pin, 1)
    GPIO.output(pin, 0)
'''


def shift_in(dec):
    dec2bin = "{0:09b}".format(dec)  # "{0:08b}" for 1 sr
    for bit in range(9):  # 8
        if dec2bin[bit] == '1':
            print('1', end='')
            # GPIO.output(dataPin, 1)
        else:
            print('0', end='')
            # GPIO.output(dataPin, 0)
    print('')
    # pulsePin(latchPin)


def print_job(droplets, push, pull):
    '''
    GPIO.output(OEPin, 0)
    time.sleep(push)
    GPIO.output(OEPin, 1)
    time.sleep(pull)
    '''
    for dot in range(droplets):
        # GPIO.output(OEPin, 0)
        print('. ', end='')
        time.sleep(push)
        # GPIO.output(OEPin, 1)
        print('', end='')
        time.sleep(pull)
    print('')
    # '''

