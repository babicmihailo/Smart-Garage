import json
import os
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from json.decoder import JSONDecodeError
import paho.mqtt.client as mqtt

# Initialize Firebase app with credentials
cred = credentials.Certificate("privateKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-garage-81733-default-rtdb.europe-west1.firebasedatabase.app/'
})

# Define path to data.json file
filePath = './data.json'

# Get a reference to the Firebase Realtime Database root
ref = db.reference()


def onConnect(client, userdata, flags, rc):
    print("Connected to broker with result code "+str(rc))
    client.subscribe("client/access")
    client.subscribe("client/distance")
    client.subscribe("client/motion")
    client.subscribe("client/pollution")
    client.subscribe("client/sound")


def controlLogic():
    data = ref.get()

    if int(data["distance"]) < 20:
        data.update({"stateParking": "on"})
    else:
        data.update({"stateParking": "off"})

    if int(time.time()) - int(data["timestampVents"])/1000 > 30:
        if 500 < int(data["pollution"]) < 1000:
            data.update({"stateVents": "on"})
        elif int(data["pollution"]) >= 1000:
            data.update({"stateSprinkler": "on"})
            data.update({"stateVents": "on"})
        else:
            data.update({"stateSprinkler": "off"})
            data.update({"stateVents": "off"})
    else:
        if int(data["pollution"]) >= 1000:
            data.update({"stateSprinkler": "on"})
        else:
            data.update({"stateSprinkler": "off"})

    if int(time.time()) - int(data["timestampLights"])/1000 > 30:
        if data["motion"] == "1":
            data.update({"stateLights": "on"})
        else:
            data.update({"stateLights": "off"})

    if int(time.time()) - int(data["timestampDoors"])/1000 > 30:
        if data["access"] == "1" or data["sound"] == "1":
            data.update({"stateDoors": "on"})
            data.update({"stateAlarm": "off"})
        elif data["access"] == "0" or data["sound"] == "0":
            data.update({"stateDoors": "off"})
            data.update({"stateAlarm": "off"})
        else:
            data.update({"stateDoors": "off"})
            data.update({"stateAlarm": "on"})
    else:
        if data["access"] == "1" or data["sound"] == "1":
            data.update({"stateAlarm": "off"})
        elif data["access"] == "0" or data["sound"] == "0":
            data.update({"stateAlarm": "off"})
        else:
            data.update({"stateAlarm": "on"})

    ref.update(data)  # write the updated data back to the database


def onMessage(client, userdata, msg):
    print("Received message on topic " + msg.topic + ": " + msg.payload.decode())
    data = ref.get()

    if "access" in msg.topic:
        data.update({"access": msg.payload.decode()})
    if "distance" in msg.topic:
        data.update({"distance": msg.payload.decode()})
    if "motion" in msg.topic:
        data.update({"motion": msg.payload.decode()})
    if "pollution" in msg.topic:
        data.update({"pollution": msg.payload.decode()})
    if "sound" in msg.topic:
        data.update({"sound": msg.payload.decode()})

    ref.update(data)  # write the updated data back to the database


def startMQTT(addr):
    try:
        client = mqtt.Client()
        client.on_connect = onConnect
        client.on_message = onMessage
        client.connect("localhost", 1883, 60)
        client.loop_start()

        while True:
            controlLogic()
            data = ref.get()
            client.publish("server/sprinkler", data["stateSprinkler"])
            client.publish("server/lights", data["stateLights"])
            client.publish("server/doors", data["stateDoors"])
            client.publish("server/vents", data["stateVents"])
            client.publish("server/alarm", data["stateAlarm"])
            client.publish("server/parking", data["stateParking"])
            time.sleep(5)
    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"Error during MQTT Publishing: {e}")
