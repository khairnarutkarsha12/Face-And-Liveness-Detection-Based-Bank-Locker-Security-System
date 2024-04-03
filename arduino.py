import serial

ser = serial.Serial('COM3',9600,timeout=0.1)
ser.setDTR(False)
ser.close()

def sendSerial(data):
    ser.open()
    ser.write(data.encode('utf-8'))
    ser.close()
