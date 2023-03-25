import time
import sys
from Adafruit_IO import MQTTClient
AIO_FEED_ID = ["temp","humid","relay1","relay2","co2","pm25","pm10","co","so2","no2"]
AIO_USERNAME = "trunggden"
AIO_KEY = "aio_qTHB11Y5kk07ir2auGP2Q0MJ1DGV"

def  connected(client):
    print("Ket noi thanh cong...")
    for feed in AIO_FEED_ID:
        client.subscribe(feed)


def  message(client , feed_id , payload):
    print("Nhan du lieu: " +payload + " feed_id " + feed_id)
    if(feed_id=="relay1" and payload=="1"):
        setDevice1(True)
    elif(feed_id=="relay1" and payload=="0"):
        setDevice1(False)
    if (feed_id == "relay2" and payload == "1"):
        setDevice2(True)
    elif (feed_id == "relay2" and payload == "0"):
        setDevice2(False)



clients = MQTTClient(AIO_USERNAME , AIO_KEY)
clients.on_connect = connected
clients.on_message = message
clients.connect()
clients.loop_background()

print("Sensors and Actuators")
import serial.tools.list_ports
def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB Serial" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort

portName = getPort()
print(portName)
if portName != "None":
    ser = serial.Serial(port=portName, baudrate=9600)

relay1_ON  = [0, 6,  0, 0, 0, 255,200, 91]
relay1_OFF = [0, 6, 0, 0, 0, 0, 136, 27]

def setDevice1(state):
    if state == True:
        ser.write(relay1_ON)
    else:
        ser.write(relay1_OFF)

relay2_ON  = [15, 6, 0, 0, 0, 255, 200, 164]
relay2_OFF = [15, 6, 0, 0, 0, 0, 136, 228]

def setDevice2(state):
    if state == True:
        ser.write(relay2_ON)
    else:
        ser.write(relay2_OFF)



def serial_read_data(ser):
    bytesToRead = ser.inWaiting()
    if bytesToRead > 0:
        out = ser.read(bytesToRead)
        data_array = [b for b in out]
        #print(data_array)
        if len(data_array) >= 7:
            array_size = len(data_array)
            value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
            return value
        else:
            return -1
    return 0


air_temperature =[3, 3, 0, 0, 0, 1, 133, 232]
def readTemperature():
    serial_read_data(ser)
    ser.write(air_temperature)
    time.sleep(2)
    value = serial_read_data(ser)
    clients.publish("temp", value/10)
    return value



air_moisture = [3, 3, 0, 1, 0, 1, 212, 40]
def readMoisture():
    serial_read_data(ser)
    ser.write(air_moisture)
    time.sleep(2)
    value = serial_read_data(ser)
    clients.publish("humid",value/10)
    return value

air_co2 = [2, 3, 0, 4, 0, 1, 197, 248]
def readCO2():
    serial_read_data(ser)
    ser.write(air_co2)
    time.sleep(2)
    value = serial_read_data(ser)
    clients.publish("co2",(value*4)/5)
    return value

air_pm25 = [ 4, 3, 0, 12, 0, 1, 68, 92]
def readPM25():
    serial_read_data(ser)
    ser.write(air_pm25)
    time.sleep(2)
    value = serial_read_data(ser)
    clients.publish("pm25",value)
    return value

air_pm10 = [4, 3, 0, 13, 0, 1, 21, 156]
def readPM10():
    serial_read_data(ser)
    ser.write(air_pm10)
    time.sleep(2)
    value = serial_read_data(ser)
    clients.publish("pm10",value)
    return value

air_NO2 = [0x0C, 0x03, 0x00, 0x02, 0x00, 0x01, 0x24, 0xD7]
def readNO2():
    serial_read_data(ser)
    ser.write(air_NO2)
    time.sleep(2)
    value = serial_read_data(ser)
    clients.publish("no2",value)
    return value

air_CO = [0x0E, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0x35]
def readCO():
    serial_read_data(ser)
    ser.write(air_CO)
    time.sleep(2)
    value = serial_read_data(ser)
    clients.publish("co",value)
    return value

air_SO2 = [0x0D, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0x06]
def readSO2():
    serial_read_data(ser)
    ser.write(air_SO2)
    time.sleep(2)
    value = serial_read_data(ser)
    clients.publish("so2",value)
    return value

sensor = 0
timer = 0

def TimerInterrup (timer):
    if timer == 5:
        ReadSensor(1)
    elif timer == 10:
        ReadSensor(2)
    elif timer == 15:
        ReadSensor(3)
    elif timer == 20:
        ReadSensor(4)
    elif timer == 25:
        ReadSensor(5)
    elif timer == 30:
        ReadSensor(6)
    elif timer == 35:
        ReadSensor(7)
    elif timer == 40:
        ReadSensor(8)

def ReadSensor(sensor):
    switcher = {
        1: print(readTemperature()),
        2: print(readMoisture()),
        3: print(readCO2()),
        4: print(readPM25()),
        5: print(readPM10()),
        6: print(readNO2()),
        7: print(readCO()),
        8: print(readSO2())
    }
    return switcher.get(sensor)


while True:
    timer = timer + 1
    if timer == 5 or timer == 10 or timer == 15 or timer == 20 or timer == 25 or timer == 30 or timer == 35 or timer == 40:
        TimerInterrup(timer)

    time.sleep(1)

    if timer >= 40:
        timer = 0
