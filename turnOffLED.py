import time
import serial

ard = serial.Serial('/dev/ttyACM0', 9600, timeout = 1)
        
def readArd():
    ret = ard.read().decode("ASCII")#line()#.decode()
    return ret

ard.write("2".encode())

while ard.inWaiting() < 1:
    continue

retu = readArd()
while retu == "3":
    print("Purging...")
    while ard.inWaiting() < 1:
        continue
    retu = readArd()
    if retu == "4":
        print("Purged")
quit()



