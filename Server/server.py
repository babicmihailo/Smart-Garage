import socket
import struct
import threading
import time
import server_mqtt

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900

SSDP_RESPONSE = """

HTTP/1.1 200 OK
CACHE-CONTROL: max-age=86400
EXT: 
LOCATION: {location}
SERVER: Controller
ST: {st}
USN: uuid:{uuid}::{st}
"""

allDevices = []
activeDevices = []


def addDevice(item):
    global allDevices
    allDevices.append(item)


def printDevices():
    global allDevices
    print(allDevices)


def printActiveDevices():
    global activeDevices
    while True:
        print(activeDevices)
        time.sleep(10)


def addToActive(item):
    global activeDevices
    activeDevices.append(item)


def deviceExists(item):
    global allDevices
    if item not in allDevices:
        addDevice(item)
    addToActive(item)


def removeFromActive(item):
    global activeDevices
    activeDevices.remove(item)


def handleClientRequest(sock, addr):
    try:
        client = [sock, addr]
        location = "http://{}:{}/".format(socket.gethostbyname(socket.gethostname()), 8080)
        st = "urn:schemas-upnp-org:device:Controller"
        uuid = "1234567890"
        response = SSDP_RESPONSE.format(location=location, st=st, uuid=uuid)
        sock.sendto(response.encode("utf-8"), addr)
        print(f"Sent SSDP response to {addr}")
        # Set the timeout to 10 seconds
        sock.settimeout(10)
        mqttThread = threading.Thread(target=server_mqtt.startMQTT, args=(addr[0],))
        if not mqttThread.is_alive():
            mqttThread.start()
        while True:
            data, addr = sock.recvfrom(1024)
            try:
                if "NOTIFY" in data.decode("utf-8"):
                    #print(f"Received NOTIFY request from {addr}")
                    if "ssdp:alive" in data.decode("utf-8"):
                        # Send response back to client
                        response = f"NOTIFY:alive transmitted"
                        sock.sendto(response.encode("utf-8"), addr)
                    elif "ssdp:byebye" in data.decode("utf-8"):
                        print(f"Received BYEBYE request from {addr}")
                        break
            except Exception as e:
                print(f"Error handling NOTIFY request: {e}")
            # Reset the timeout
            sock.settimeout(10)

    except socket.timeout:
        print(f"Client {addr} timed out")

    except Exception as e:
        print(f"Error handling client request: {e}")

    finally:
        try:
            sock.close()
            removeFromActive(client)
            mqttThread._stop()
            print("Client disconnected.")
        except Exception as e:
            print(e)


def startSsdpServer():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", SSDP_PORT))
        group = socket.inet_aton(SSDP_ADDR)
        mreq = struct.pack("4sL", group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            data, addr = sock.recvfrom(1024)
            try:
                if "M-SEARCH" in data.decode("utf-8"):
                    if "urn:schemas-upnp-org:device:Sensors" in data.decode("utf-8"):
                        print(f"Received M-SEARCH request from {addr}")
                        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        client_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        client_sock.bind(("", 0))
                        client = [client_sock, addr]
                        deviceExists(client)
                        # Handle client request in a separate thread
                        clientThread = threading.Thread(target=handleClientRequest, args=(client_sock, addr))
                        clientThread.start()
            except Exception as e:
                print(f"Error handling client request: {e}")
    except socket.error as e:
        print(f"Socket error: {e}")
    except KeyboardInterrupt:
        pass
    finally:
        try:
            clientThread._stop()
        except Exception:
            print("Client hopefully terminated.")


# https://we.tl/t-dOj0k4s3lS
startSsdpServer()
