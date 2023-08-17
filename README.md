# IoT Smart Garage Project

![GitHub License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)

Welcome to the IoT Smart Garage Project! This project combines hardware and software components to create an intelligent garage system. It leverages SSDP and MQTT protocols, Arduino sensors, cloud integration, and an Android application for seamless control and monitoring of your garage. With sensors like proximity, sound, movement, gas, and RFID, the project achieves smart management of lights, alarms, safety systems, and automatic garage opening/closing.

## Features

- **SSDP Protocol**: The project employs the SSDP (Simple Service Discovery Protocol) to enable automatic discovery of devices, making it effortless to locate and connect with the garage sensor unit.

- **MQTT Communication**: The sensor unit collects data and communicates with the controller using the MQTT (Message Queuing Telemetry Transport) protocol. This ensures efficient and reliable data transmission.

- **Arduino Sensors**: The garage sensor unit is equipped with a variety of sensors including:
  - Proximity sensor for detecting objects & parking assistance.
  - Sound sensor for audio monitoring.
  - Movement sensor for motion detection.
  - Gas sensor for air quality assessment & hazard detection.
  - RFID sensor for access control.
  
- **Smart Management**: The collected data from the sensors enables smart management of lights, alarms, safety systems, and automatic garage door opening/closing.

- **System Control**: The controller, written in Python, processes the sensor data and orchestrates the functioning of the garage door actuators. This allows for remote and automated garage door control.

- **Cloud Integration**: The controller communicates with a Firebase database hosted in the cloud. The data collected from the garage sensors is stored and retrieved through this cloud integration.

- **User Android Application**: An Android application, developed in Java, offers users an intuitive interface to monitor and control their garage. It displays the garage status, allows door, lights, air conditioning control, and provides alerts based on sensor data.

- **MQTT Broker (HiveMQ)**: HiveMQ is used as the MQTT broker for facilitating communication between the garage sensor unit and the controller.

## How to Use

1. **Hardware Setup**: Assemble the garage sensor unit with Arduino sensors (proximity, sound, movement, gas, RFID) and connect them to your controller unit.

2. **Software Configuration**: Configure the Arduino code for the sensor unit to communicate with the controller using the MQTT protocol. Set up the Python controller code to process sensor data and interact with the Firebase database. Adjust the Android app to connect with the Firebase database and MQTT broker.

3. **Firebase Setup**: Create a Firebase project and set up a real-time database to store sensor data and garage status. Obtain the necessary API keys for secure communication.

4. **Android Application**: Install the provided Android application on your smartphone. Configure the app to connect to your Firebase project using the API keys.

5. **MQTT Broker Configuration (HiveMQ)**: Set up HiveMQ as the MQTT broker and configure it to handle the MQTT communication between the garage sensor unit and the controller.

6. **Discover Devices**: The Controller uses SSDP to automatically discover and connect to the garage sensor unit.

7. **Monitor and Control**: Controller automaticlly controls the system, and user can use the Android application to monitor the garage status, receive alerts, and control the garage door actuators remotely.

