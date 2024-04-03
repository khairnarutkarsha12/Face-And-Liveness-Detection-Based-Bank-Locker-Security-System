import serial


#ser.close()

def sendSerial(data):
    ser = serial.Serial('COM4',9600,timeout=0.1)
    ser.setDTR(False)
    #ser.open()
    ser.write(data.encode('utf-8'))
    ser.close()

sendSerial('O')