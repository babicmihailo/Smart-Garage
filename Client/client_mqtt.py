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
stateActivity = "off"


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


def setActivity(newValue):
    global stateActivity
    stateActivity = newValue


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
        #print("Alarm is on")
        ser.write(b'L')
    else:
        ser.write(b'H')
        #print("Alarm is off")
    if stateDoors == "on":
        #print("Doors are open")
        pass
    else:
        #print("Doors are closed")
        pass
    if stateLights == "on":
        #print("Lights are on")
        pass
    else:
        #print("Lights are off")
        pass
    if stateSprinkler == "on":
        #print("Sprinklers on")
        pass
    else:
        #print("Sprinklers off")
        pass
    if stateVents == "on":
        #print("Vents are on")
        pass
    else:
        #print("Vents are off")
        pass
    counter = 0
    if "on" in stateParking and "off" in stateAlarm:
        while counter < 10:
            ser.write(b'L')
            time.sleep(0.25)
            ser.write(b'H')
            time.sleep(0.25)
            counter += 1
    elif "off" in stateParking and "off" in stateAlarm:
        ser.write(b'H')
        time.sleep(5)


def onConnect(client, userdata, flags, rc):
    print("Connected to broker with result code " + str(rc))
    client.subscribe("server/sprinkler")
    client.subscribe("server/lights")
    client.subscribe("server/doors")
    client.subscribe("server/vents")
    client.subscribe("server/alarm")
    client.subscribe("server/parking")
    client.subscribe("server/activity")


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
    if "activity" in msg.topic:
        setActivity(msg.payload.decode())
        print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")


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
            try:
                if(stateActivity == "active"):
                    client.publish("client/access", str(access))
                    client.publish("client/distance", str(distance))
                    client.publish("client/motion", str(motion))
                    client.publish("client/pollution", str(pollution))
                    client.publish("client/sound", str(sound))
                    actuatorsLogic()
                else:
                    print("Device is sleeping/inactive")
                    print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
                    time.sleep(5)
            except KeyboardInterrupt:
                break

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error during MQTT Publishing: {e}")
    finally:
        serialThread._stop()
        client.loop_stop()
        client.disconnect()