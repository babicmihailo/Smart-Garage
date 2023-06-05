import socket
import time
import client_mqtt
import threading

SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
SSDP_MX = 1

SSDP_REQUEST = """

M-SEARCH * HTTP/1.1
HOST: {}:{}
MAN: "ssdp:discover"
MX: {}
ST: {}
NT: {}
"""

SSDP_ALIVE_NOTIFY = """
NOTIFY * HTTP/1.1
HOST: {}:{}
NTS: ssdp:alive
NT: {}
USN: {}
LOCATION: {}
CACHE-CONTROL: {}
SERVER: {}
"""

SSDP_BYEBYE_NOTIFY = """
NOTIFY * HTTP/1.1
HOST: {}:{}
NTS: ssdp:byebye
NT: {}
USN: {}
"""


def sendNotifyAlive(sock, addr, st):
    notify = SSDP_ALIVE_NOTIFY.format(SSDP_ADDR, SSDP_PORT, st, "Sensors", "http://" + addr[0] + ":" + str(addr[1]),
             "max-age=1800", "Controller")
    sock.sendto(notify.encode("utf-8"), addr)
    response, sock = sock.recvfrom(1024)
    #print(response)


def sendNotifyByeBye(sock, addr, st):
    notify = SSDP_BYEBYE_NOTIFY.format(SSDP_ADDR, SSDP_PORT, st, "Sensors")
    sock.sendto(notify.encode("utf-8"), addr)
    print(notify)


def discoverSsdpDevices():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", 0))
        sock.settimeout(2)

        while True:
            for st in ["ssdp:all", "urn:schemas-upnp-org:device:Controller"]:
                request = SSDP_REQUEST.format(SSDP_ADDR, SSDP_PORT, SSDP_MX, st, "urn:schemas-upnp-org:device:Sensors")
                sock.sendto(request.encode("utf-8"), (SSDP_ADDR, SSDP_PORT))
                print(request)
                try:
                    data, addr = sock.recvfrom(1024)
                    if "Controller" in data.decode("utf-8"):
                        print(data.decode(), addr)
                        break
                except socket.timeout:
                    pass

            # Send NOTIFY every 5 seconds
            mqtt = threading.Thread(target=client_mqtt.startMQTT, args=(addr[0],))
            mqtt.start()
            while True:
                try:
                    for st in ["ssdp:all", "urn:schemas-upnp-org:device:Controller"]:
                        sendNotifyAlive(sock, addr, st)
                    time.sleep(5)
                except KeyboardInterrupt:
                    for st in ["ssdp:all", "urn:schemas-upnp-org:device:Controller"]:
                        sendNotifyByeBye(sock, addr, st)
                        mqtt._stop()
                except Exception as e:
                    print("Error occurred while closing thread: ", e)

    except Exception as e:
        print("Error occurred while discovering devices: ", e)


discoverSsdpDevices()
