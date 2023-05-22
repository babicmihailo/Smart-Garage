import time
import serial
import threading
import paho.mqtt.client as mqtt


# initialize global variables
ser = serial.Serial('COM3', 9600)

motion = 0
pollution = 0
distance = 0
sound = 0
access = 0

stateAlarm = "off"
stateDoors = "off"
stateLights = "off"
stateSprinkler = "off"
stateParking = "off"
stateVents = "off"


def setAlarm(newValue):
    global stateAlarm
    stateAlarm = newValue


def setParking(newValue):
    global stateParking
    stateParking = newValue


def setVents(newValue):
    global stateVents
    stateVents = newValue


def setDoors(newValue):
    global stateDoors
    stateDoors = newValue


def setLights(newValue):
    global stateLights
    stateLights = newValue


def setSprinkler(newValue):
    global stateSprinkler
    stateSprinkler = newValue


def setMotion(newValue):
    global motion
    motion = newValue


def setPollution(newValue):
    global pollution
    pollution = newValue


def setDistance(newValue):
    global distance
    distance = newValue


def setSound(newValue):
    global sound
    sound = newValue


def setAccess(newValue):
    global access
    access = newValue


def serialReading():
    while True:
        try:
            # read data from serial port
            rawData = ""
            while True:
                c = ser.read().decode('utf-8')
                if c == '\n':
                    break
                rawData += c
            rawData = rawData.strip()

            # parse data and update global variables
            key, value = rawData.split(': ')
            if key == 'distance':
                if int(value) != distance:
                    setDistance(int(value))
            elif key == 'pollution':
                if int(value) != pollution:
                    setPollution(int(value))
            elif key == 'sound':
                if int(value) != sound:
                    setSound(int(value))
            elif key == 'motion':
                if int(value) != motion:
                    setMotion(int(value))
            elif key == 'access':
                if int(value) != access:
                    setAccess(int(value))

        except UnicodeDecodeError:
            continue

        except KeyboardInterrupt:
            # close serial port and exit program
            ser.close()
            break


def actuatorsLogic():

    if stateAlarm == "on":
        ser.write(b'L')
    else:
        ser.write(b'H')
    if stateDoors == "on":
        pass
        #openDoors(60)
    else:
        pass
    if stateLights == "on":
        pass
        #turnOnLights(60)
    else:
        pass
    if stateSprinkler == "on":
        pass
        #turnOnSplinkler
        #callEmergency
    else:
        pass
    if stateVents == "on":
        pass
        #turnOnVents
    else:
        pass
        #turnOffVents
    counter = 0
    if "on" in stateParking:
        while(counter < 10):
            ser.write(b'L')
            time.sleep(0.25)
            ser.write(b'H')
            time.sleep(0.25)
            counter += 1
    else:
        ser.write(b'H')
        time.sleep(5)


def onConnect(client, userdata, flags, rc):
    print("Connected to broker with result code "+str(rc))
    client.subscribe("server/sprinkler")
    client.subscribe("server/lights")
    client.subscribe("server/doors")
    client.subscribe("server/vents")
    client.subscribe("server/alarm")
    client.subscribe("server/parking")


def onMessage(client, userdata, msg):
    print("Received message on topic "+msg.topic+": "+msg.payload.decode())
    if "sprinkler" in msg.topic:
        setSprinkler(msg.payload.decode())
    if "lights" in msg.topic:
        setLights(msg.payload.decode())
    if "doors" in msg.topic:
        setDoors(msg.payload.decode())
    if "vents" in msg.topic:
        setVents(msg.payload.decode())
    if "alarm" in msg.topic:
        setSound(msg.payload.decode())
    if "parking" in msg.topic:
        setParking(msg.payload.decode())


def startMQTT(addr):
    try:
        serialThread = threading.Thread(target=serialReading)
        serialThread.start()
        client = mqtt.Client()
        client.on_connect = onConnect
        client.on_message = onMessage
        print(addr)
        client.connect(addr, 1883, 60)
        client.loop_start()

        while True:
            client.publish("client/access", str(access))
            client.publish("client/distance", str(distance))
            client.publish("client/motion", str(motion))
            client.publish("client/pollution", str(pollution))
            client.publish("client/sound", str(sound))
            actuatorsLogic()
    except KeyboardInterrupt:
        serialThread._stop()
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"Error during MQTT Publishing: {e}")