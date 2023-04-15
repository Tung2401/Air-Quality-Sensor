
import time
import sys
import array as arr
import sqlite3
from array import *
from Adafruit_IO import MQTTClient
AIO_FEED_ID = ["temp","humid","relay1","relay2","co2","pm25","pm10","co0","so2","no2","aqi"]
AIO_USERNAME = "trunggden"
AIO_KEY = "aio_XhLM29zMp0167GZAWKvF5qVlOval"


I = arr.array('i',[0,50,100,150,200,300,400,500])

bpCO = arr.array('i',[0,10000,30000,45000,60000,90000,120000,150000])
bpSO2 = arr.array('i',[0,125,350,550,800,1600,2100,2630])
bpNO2 = arr.array('i',[0,100,200,700,1200,2350,3100,3850])
bpPM10 = arr.array('i',[0,50,150,250,350,420,500,600])
bpPM25 = arr.array('i',[0,25,50,80,150,250,350,500])

arrAQI = [0] * 5 #0: PM2.5 // 1: PM10 // 2: CO // 3: NO2 // 4: SO2
Ii = 0
Ii1 = 0
totalNO2 = 0
totalSO2 = 0
totalCO = 0

maxAQI = 0
max_index = 0
avgNO2 = 0
avgSO2 = 0
avgCO = 0

AQIPM25 = 0
AQIPM10 = 0
AQICO = 0
AQISO2 = 0
AQINO2 = 0

countNO2 = 0
countSO2 = 0
countCO = 0
countCO2 = 0
countPM25 = 0
countPM10 = 0

arrPM25 = [0] * 60
arrPM10 = [0] * 60

nowCastPM25 = 0
nowCastPM10 = 0

wPM25 = 0
wPM10 = 0
y1 = 0
y2 = 0
y0 = 0


countDay1=0
countDay2=0
countDay3=0

conn = sqlite3.connect('AQIdata1.db')

# conn.execute('''CREATE TABLE AQIData1(
#                 hour REAL PRIMARY KEY NOT NULL,
#                 AQI_DATA REAL NOT NULL);''')

conn1 = sqlite3.connect('AQIdata2.db')

# conn1.execute('''CREATE TABLE AQIData2(
#                 hour REAL PRIMARY KEY NOT NULL,
#                 AQI_DATA REAL NOT NULL);''')

conn2 = sqlite3.connect('AQIdata3.db')

# conn2.execute('''CREATE TABLE AQIData3(
#                 hour REAL PRIMARY KEY NOT NULL,
#                 AQI_DATA REAL NOT NULL);''')

cursor = conn.cursor()
cursor1 = conn1.cursor()
cursor2 = conn2.cursor()


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
        if "USB Serial Port" in strPort:
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
    time.sleep(1)
    value = serial_read_data(ser)
    clients.publish("temp", value/10)
    return value



air_moisture = [3, 3, 0, 1, 0, 1, 212, 40]
def readMoisture():
    serial_read_data(ser)
    ser.write(air_moisture)
    time.sleep(1)
    value = serial_read_data(ser)
    clients.publish("humid",value/10)
    return value

air_co2 = [2, 3, 0, 4, 0, 1, 197, 248]
def readCO2():
    global countCO2
    serial_read_data(ser)
    ser.write(air_co2)
    time.sleep(1)
    value = serial_read_data(ser)
    clients.publish("co2",(value*4)/5)
    countCO2 += 1
    return value

air_pm25 = [ 4, 3, 0, 12, 0, 1, 68, 92]
def readPM25():
    global arrPM25,countPM25
    serial_read_data(ser)
    ser.write(air_pm25)
    time.sleep(1)
    value = serial_read_data(ser)
    arrPM25[countPM25] = value
    clients.publish("pm25",value)
    countPM25 += 1
    return value

air_pm10 = [4, 3, 0, 13, 0, 1, 21, 156]
def readPM10():
    global arrPM10, countPM10
    serial_read_data(ser)
    ser.write(air_pm10)
    time.sleep(1)
    value = serial_read_data(ser)
    arrPM10[countPM10] = value
    clients.publish("pm10",value)
    countPM10 += 1
    return value

air_NO2 = [0x0C, 0x03, 0x00, 0x02, 0x00, 0x01, 0x24, 0xD7]
def readNO2():
    global totalNO2,countNO2
    serial_read_data(ser)
    ser.write(air_NO2)
    time.sleep(1)
    value = serial_read_data(ser)
    totalNO2 += value
    clients.publish("no2",value)
    countNO2 += 1
    return value

air_CO = [0x0E, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0x35]
def readCO():
    global totalCO,countCO
    serial_read_data(ser)
    ser.write(air_CO)
    time.sleep(1)
    value = serial_read_data(ser)
    totalCO += value
    clients.publish("co0",value)
    countCO += 1
    return value

air_SO2 = [0x0D, 0x03, 0x00, 0x02, 0x00, 0x01, 0x25, 0x06]
def readSO2():
    global totalSO2,countSO2
    serial_read_data(ser)
    ser.write(air_SO2)
    time.sleep(1)
    value = serial_read_data(ser)
    totalSO2 += value
    clients.publish("so2",value)
    countSO2 += 1
    return value

sensor = 0
timer = 0

def TimerInterrup (timer):
    global countCO2, countPM25, countPM10, countNO2, countCO, countSO2, totalCO, totalNO2
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

def returnDefault():
    global countCO2, countPM25, countPM10, countNO2, countCO, countSO2, totalNO2, totalCO,totalSO2, avgNO2, avgCO, avgSO2, wPM10, wPM25
    totalNO2 = 0
    totalSO2 = 0
    totalCO = 0

    Ii = 0
    Ii1 = 0
    avgNO2 = 0
    avgSO2 = 0
    avgCO = 0
    arrAQI = [0] * 5
    countNO2 = 0
    countSO2 = 0
    countCO = 0
    countCO2 = 0
    countPM25 = 0
    countPM10 = 0

    wPM25 = 0
    wPM10 = 0

def calculateAvg():
    global avgCO, avgNO2, avgSO2
    avgCO = totalCO
    avgSO2 = totalSO2
    avgNO2 = totalNO2

def CalculateNowcastPM25():
    global nowCastPM25,arrPM25,wPM25
    min = arrPM25[0]
    max = arrPM25[0]
    for i in arrPM25:
        if min > i:
            min = i
        elif max < i:
            max = i
    wPM25 = min / max
    if wPM25 <= 0.5:
        wPM25 = 0.5
        nowCastPM25 = (wPM25**0)*arrPM25[59]+(wPM25**1)*arrPM25[54]+(wPM25**2)*arrPM25[49]+(wPM25**3)*arrPM25[44]+(wPM25**4)*arrPM25[39]+(wPM25**5)*arrPM25[34]+(wPM25**6)*arrPM25[29]+(wPM25**7)*arrPM25[24]+(wPM25**8)*arrPM25[19]++(wPM25**9)*arrPM25[14]+(wPM25**10)*arrPM25[9]+(wPM25**11)*arrPM25[4]
    elif wPM25 > 0.5:
        nowCastPM25 = ((wPM25**0)*arrPM25[59]+(wPM25**1)*arrPM25[54]+(wPM25**2)*arrPM25[49]+(wPM25**3)*arrPM25[44]+(wPM25**4)*arrPM25[39]+(wPM25**5)*arrPM25[34]+(wPM25**6)*arrPM25[29]+(wPM25**7)*arrPM25[24]+(wPM25**8)*arrPM25[19]++(wPM25**9)*arrPM25[14]+(wPM25**10)*arrPM25[9]+(wPM25**11)*arrPM25[4])/(wPM25**0+wPM25**1+wPM25**2+wPM25**3+wPM25**4+wPM25**5+wPM25**6+wPM25**7+wPM25**8+wPM25**9+wPM25**10+wPM25**11)


def CalculateNowcastPM10():
    global nowCastPM10, arrPM10, wPM10
    min = arrPM10[0]
    max = arrPM10[0]
    for i in arrPM10:
        if min > i:
            min = i
        elif max < i:
            max = i
    wPM10 = min / max
    if wPM10 <= 0.5:
        wPM10 = 0.5
        nowCastPM10 = (wPM10 ** 0) * arrPM10[59] + (wPM10 ** 1) * arrPM10[54] + (wPM10 ** 2) * arrPM10[49] + (wPM10 ** 3) * arrPM10[44] + (wPM10 ** 4) * arrPM10[39] + (wPM10 ** 5) * arrPM10[34] + (wPM10 ** 6) * arrPM10[29] + (wPM10 ** 7) * arrPM10[24] + (wPM10 ** 8) * arrPM10[19] + +(wPM10 ** 9) * arrPM10[14] + (wPM10 ** 10) * arrPM10[9] + (wPM10 ** 11) * arrPM10[4]
    elif wPM10 > 0.5:
        nowCastPM10 = ((wPM10 ** 0) * arrPM10[59] + (wPM10 ** 1) * arrPM10[54] + (wPM10 ** 2) * arrPM10[49] + (wPM10 ** 3) *arrPM10[44] + (wPM10 ** 4) * arrPM10[39] + (wPM10 ** 5) * arrPM10[34] + (wPM10 ** 6) * arrPM10[29] + (wPM10 ** 7) * arrPM10[24] + (wPM10 ** 8) * arrPM10[19] + +(wPM10 ** 9) * arrPM10[14] + (wPM10 ** 10) * arrPM10[9] + (wPM10 ** 11) * arrPM10[4]) / (wPM10 ** 0 + wPM10 ** 1 + wPM10 ** 2 + wPM10 ** 3 + wPM10 ** 4 + wPM10 ** 5 + wPM10 ** 6 + wPM10 ** 7 + wPM10 ** 8 + wPM10 ** 9 + wPM10 ** 10 + wPM10 ** 11)


def calculateAQIPM25():
    global nowCastPM25,AQIPM25,I,Ii1,Ii,bpPM25,arrAQI
    AQIPM25 = ((I[Ii1]-I[Ii]) / (bpPM25[Ii1] - bpPM25[Ii]))*(nowCastPM25-bpPM25[Ii]) + I[Ii]
    arrAQI[0] = AQIPM25
def IPM25():
    global nowCastPM25,Ii,Ii1,bpPM25
    if bpPM25[0] <= nowCastPM25 < bpPM25[1]:
        Ii = 0
        Ii1 = 1
        calculateAQIPM25()
    elif bpPM25[1] <= nowCastPM25 < bpPM25[2]:
        Ii = 1
        Ii1 = 2
        calculateAQIPM25()
    elif bpPM25[2] <= nowCastPM25 < bpPM25[3]:
        Ii = 2
        Ii1 = 3
        calculateAQIPM25()
    elif bpPM25[3] <= nowCastPM25 < bpPM25[4]:
        Ii = 3
        Ii1 = 4
        calculateAQIPM25()
    elif bpPM25[4] <= nowCastPM25 < bpPM25[5]:
        Ii = 4
        Ii1 = 5
        calculateAQIPM25()
    elif bpPM25[5] <= nowCastPM25 < bpPM25[6]:
        Ii = 5
        Ii1 = 6
        calculateAQIPM25()
    elif bpPM25[6] <= nowCastPM25 < bpPM25[7]:
        Ii = 6
        Ii1 = 7
        calculateAQIPM25()

def calculateAQIPM10():
    global nowCastPM10, AQIPM10, I, Ii1, Ii, bpPM10, arrAQI
    AQIPM10 = ((I[Ii1] - I[Ii]) / (bpPM10[Ii1] - bpPM10[Ii])) * (nowCastPM10 - bpPM10[Ii]) + I[Ii]
    arrAQI[1] = AQIPM10

def IPM10():
    global nowCastPM10, Ii, Ii1, bpPM10
    if bpPM10[0] <= nowCastPM10 < bpPM10[1]:
        Ii = 0
        Ii1 = 1
        calculateAQIPM10()
    elif bpPM10[1] <= nowCastPM10 < bpPM10[2]:
        Ii = 1
        Ii1 = 2
        calculateAQIPM10()
    elif bpPM10[2] <= nowCastPM10 < bpPM10[3]:
        Ii = 2
        Ii1 = 3
        calculateAQIPM10()
    elif bpPM10[3] <= nowCastPM10 < bpPM10[4]:
        Ii = 3
        Ii1 = 4
        calculateAQIPM10()
    elif bpPM10[4] <= nowCastPM10 < bpPM10[5]:
        Ii = 4
        Ii1 = 5
        calculateAQIPM10()
    elif bpPM10[5] <= nowCastPM10 < bpPM10[6]:
        Ii = 5
        Ii1 = 6
        calculateAQIPM10()
    elif bpPM10[6] <= nowCastPM10 < bpPM10[7]:
        Ii = 6
        Ii1 = 7
        calculateAQIPM10()


def calculateAQICO():
    global Ii,I,Ii1,avgCO,bpCO,AQICO,arrAQI
    AQICO = ((I[Ii1] - I[Ii]) / (bpCO[Ii1] - bpCO[Ii])) * (avgCO - bpCO[Ii]) + I[Ii]
    arrAQI[2] = AQICO

def ICO():
    global Ii,bpCO,Ii1,avgCO
    if bpCO[0] <= avgCO < bpCO[1]:
        Ii = 0
        Ii1 = 1
        calculateAQICO()
    elif bpCO[1] <= avgCO < bpCO[2]:
        Ii = 1
        Ii1 = 2
        calculateAQICO()
    elif bpCO[2] <= avgCO < bpCO[3]:
        Ii = 2
        Ii1 = 3
        calculateAQICO()
    elif bpCO[3] <= avgCO < bpCO[4]:
        Ii = 3
        Ii1 = 4
        calculateAQICO()
    elif bpCO[4] <= avgCO < bpCO[5]:
        Ii = 4
        Ii1 = 5
        calculateAQICO()
    elif bpCO[5] <= avgCO < bpCO[6]:
        Ii = 5
        Ii1 = 6
        calculateAQICO()
    elif bpCO[6] <= avgCO < bpCO[7]:
        Ii = 6
        Ii1 = 7
        calculateAQICO()


def calculateAQINO2():
    global Ii, I, Ii1, avgNO2, bpNO2, AQINO2, arrAQI
    AQINO2 = ((I[Ii1] - I[Ii]) / (bpNO2[Ii1] - bpNO2[Ii])) * (avgNO2 - bpNO2[Ii]) + I[Ii]
    arrAQI[3] = AQINO2

def INO2():
    global Ii, bpNO2, Ii1, avgNO2
    if bpNO2[0] <= avgNO2 < bpNO2[1]:
        Ii = 0
        Ii1 = 1
        calculateAQINO2()
    elif bpNO2[1] <= avgNO2 < bpNO2[2]:
        Ii = 1
        Ii1 = 2
        calculateAQINO2()
    elif bpNO2[2] <= avgNO2 < bpNO2[3]:
        Ii = 2
        Ii1 = 3
        calculateAQINO2()
    elif bpNO2[3] <= avgNO2 < bpNO2[4]:
        Ii = 3
        Ii1 = 4
        calculateAQINO2()
    elif bpNO2[4] <= avgNO2 < bpNO2[5]:
        Ii = 4
        Ii1 = 5
        calculateAQINO2()
    elif bpNO2[5] <= avgNO2 < bpNO2[6]:
        Ii = 5
        Ii1 = 6
        calculateAQINO2()
    elif bpNO2[6] <= avgNO2 < bpNO2[7]:
        Ii = 6
        Ii1 = 7
        calculateAQINO2()


def calculateAQISO2():
    global Ii, I, Ii1, avgSO2, bpSO2, AQISO2, arrAQI
    AQISO2 = ((I[Ii1] - I[Ii]) / (bpSO2[Ii1] - bpSO2[Ii])) * (avgSO2 - bpSO2[Ii]) + I[Ii]
    arrAQI[4] = AQISO2

def ISO2():
    global Ii, bpSO2, Ii1, avgSO2
    if bpSO2[0] <= avgSO2 < bpSO2[1]:
        Ii = 0
        Ii1 = 1
        calculateAQISO2()
    elif bpSO2[1] <= avgSO2 < bpSO2[2]:
        Ii = 1
        Ii1 = 2
        calculateAQISO2()
    elif bpSO2[2] <= avgSO2 < bpSO2[3]:
        Ii = 2
        Ii1 = 3
        calculateAQISO2()
    elif bpSO2[3] <= avgSO2 < bpSO2[4]:
        Ii = 3
        Ii1 = 4
        calculateAQISO2()
    elif bpSO2[4] <= avgSO2 < bpSO2[5]:
        Ii = 4
        Ii1 = 5
        calculateAQISO2()
    elif bpSO2[5] <= avgSO2 < bpSO2[6]:
        Ii = 5
        Ii1 = 6
        calculateAQISO2()
    elif bpSO2[6] <= avgSO2 < bpSO2[7]:
        Ii = 6
        Ii1 = 7
        calculateAQISO2()
def insertDataTable3(countDay3):
    global maxAQI
    conn2.execute("UPDATE AQIData3 SET AQI_DATA =? WHERE hour=?", (maxAQI, countDay3))
    conn2.commit()
def insertDataTable2():
    global maxAQI, countDay2
    conn1.execute("INSERT INTO AQIData2 (hour,AQI_DATA) VALUES (?,?)", (countDay2, maxAQI))
    conn1.commit()
def insertDataTable1():
    global maxAQI,countDay1
    conn.execute("INSERT INTO AQIData1 (hour,AQI_DATA) VALUES (?,?)", (countDay1, maxAQI))
    conn.commit()

countAQI = 0

def changeDatabase():
    cursor1.execute("SELECT * FROM AQIData2")
    row = cursor1.fetchall()
    for i in row:
        conn.execute("UPDATE AQIData1 SET AQI_DATA =? WHERE hour=?", (i[1], i[0]))
    conn.commit()
    cursor2.execute("SELECT * FROM AQIData3")
    row2 = cursor2.fetchall()
    for i in row2:
        conn1.execute("UPDATE AQIData2 SET AQI_DATA =? WHERE hour=?", (i[1], i[0]))
    conn1.commit()
    c = conn2.cursor()
    c.execute("SELECT * FROM AQIData3")
    row3 = c.fetchall()
    for i in row3:
        conn2.execute("UPDATE AQIData3 SET AQI_DATA =? WHERE hour=?", (0, i[0]))
    conn2.commit()

def findMaxAQI():
    global countAQI,countDay1,countDay2,countDay3
    if countDay3 >= 24:
        countDay3 = 0
        changeDatabase()
        interpolationCalculation()
    countAQI += 1
    global maxAQI,max_index,arrAQI
    maxAQI = arrAQI[0]
    for i in arrAQI:
        if maxAQI < i:
            maxAQI = i
            max_index = arrAQI.index(i)
    x = round(maxAQI)
    maxAQI = x
    clients.publish("aqi",maxAQI)
    if countDay1 < 24:
        insertDataTable1()
        countDay1 += 1
    elif countDay2 < 24:
        insertDataTable2()
        if countDay2 + 1 == 24:
            interpolationCalculation()
        countDay2 += 1
    else:
        insertDataTable3(countDay3)
        countDay3 += 1


def interpolationCalculation():
    global y1,y2,y0
    counter = 0
    counter1 = 0
    while counter < 24:
        cursor.execute("SELECT AQI_DATA FROM AQIData1 WHERE hour=?",(counter,))
        row = cursor.fetchone()
        y1 = row[0]
        cursor1.execute("SELECT AQI_DATA FROM AQIData2 WHERE hour=?", (counter1,))
        row1 = cursor1.fetchone()
        y2 = row1[0]
        y0 = y1 + 2*(y2-y1)
        if y0 <= 0:
            y0 = 0
        conn2.execute("INSERT INTO AQIData3 (hour,AQI_DATA) VALUES (?,?)", (counter, y0))
        conn2.commit()
        counter += 1
        counter1 += 1



count = 0
while True:
    timer = timer + 1
    if timer == 5 or timer == 10 or timer == 15 or timer == 20 or timer == 25 or timer == 30 or timer == 35 or timer == 40:
        TimerInterrup(timer)
    changeDatabase()
    print(countSO2)
    time.sleep(1)
    if countSO2 == 60:
        calculateAvg()
        CalculateNowcastPM25()
        CalculateNowcastPM10()
        print(nowCastPM25,nowCastPM10,totalCO,totalNO2,totalSO2)
        IPM25()
        IPM10()
        ICO()
        INO2()
        ISO2()
        findMaxAQI()
        print(maxAQI,max_index)
        returnDefault()
        time.sleep(1)
    if timer >= 40:
        timer = 0
