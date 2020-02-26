import time, threading
#import serial
#import random as rnd

#ser = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)

heartbeatHz = 1
led = 0

def hz30():
	#print(rnd.randint(0, 10))
	global led
	if led == 0:
		led = 1
	else:
		led = 0
	#threading.Timer(heartbeatHz, hz30).start()
	#return led
timerThread = threading.Thread(target=hz30)
timerThread.daemon = True
timerThread.start()
hz30()

led = 2
while True:
	if led == 2:
		led = 1
	else:
		led = 2
	print("LED: " + str(led))
	#a = ser.write(led)
	time.sleep(1)