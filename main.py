import socket
import network
import time
from machine import Pin, PWM
import json
import _thread

secondThreadInfo = {}
secondThread = []

deviceData = {
    "name":"Luka's LEDs",
    "options":{
        "Internal_led":{"pins":{"LED": "LED"},
        "modes":{
            "Digital":["pins"]
            }
        },
        "First_led":{"pins":{"Red":12,"Green":18,"Blue":2},
        "modes":{
            "PWM":["pins"],
            "Digital":["pins"],
            "Blinker PWM":["Time","pins"],
            "Blinker digital":["Time","pins"]
            }
        }
    }
}

SSID1 = "ABACUS."
PASSWORD1 = "HejkajpaDanesdogaja159"

SSID2 = "rp-pico"
PASSWORD2 = "rp-pico246"

HOST = "188.230.153.147"
PORT = 5050

FORMAT = "utf-8"
HEADER = 64

def connect(ssid, password):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        while wlan.isconnected() == False:
            time.sleep(1)
        ip = wlan.ifconfig()[0]
        return wlan

connect(SSID2, PASSWORD2)

class Server():
    def __init__(self, host, port, deviceData):
        self.deviceData = deviceData
        self.host = host
        self.port = port
        self.s = ""
        
    def serverSetup(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connectSocket(self):
        self.serverSetup()
        self.s.connect((self.host, self.port))
        data = json.dumps(self.deviceData).encode(FORMAT)
        self.s.send(data)

    def reciveCommands(self):
        messageLength = self.s.recv(64).decode(FORMAT)
        messageLength = int(messageLength)
        data = json.loads(self.s.recv(messageLength).decode(FORMAT))
        return data
        
    def secondCoreBlinker(self):
        while True:
            timeOut = secondThreadInfo["Time"]
            if timeOut == 0:
                break
            if timeOut > 3:
                secondThreadInfo["Time"] = 3
            if timeOut < 0.01:
                secondThreadInfo["Time"] = 0.01
            for pin, value in secondThreadInfo["pinValues"].items():
                if value != 0:
                    self.pwmWrite(pin, value)
                else:
                    del secondThreadInfo["pinValues"][pin]
            time.sleep(timeOut)
            for pin, value in secondThreadInfo["pinValues"].items():
                self.pwmWrite(pin, 0)
            time.sleep(timeOut)
        secondThread = []
        
    def digitalWrite(self, pin, value):
            usedPin = Pin(pin, Pin.OUT)
            usedPin.value(value)
            
    def pwmWrite(self,pin, value):
        usedPin = PWM(Pin(pin))
        usedPin.freq(1000)
        usedPin.duty_u16(value) # *655,35 so it can accept values from 0 to 100
        
    def blinker(self, command):
        print(command)
        secondThreadInfo["Time"] = command["Time"]
        secondThreadInfo["pinValues"] = command["pinValues"]
        print(secondThreadInfo["Time"])
        if secondThread == "":
            secondThread[0] = _thread.start_new_thread(self.secondCoreBlinker, ())               
            
    def handleCommands(self, commands):
        for command in commands:
            mode = command["mode"]
            if mode == "Blinker":
                command["Time"] = float(command["pinValues"].pop("Time"))
                for pin, value in command["pinValues"].items():
                    if pin != "LED":
                        pinValue = command["pinValues"].pop(pin)
                        pin = int(pin)
                        command["pinValues"][pin] = pinValue
                self.blinker(command=command)
            else:
                for pin, value in command["pinValues"].items():
                    if pin != "LED":
                        pin = int(pin)
                    if mode == "PWM":
                        self.pwmWrite(pin, value)
                    elif mode == "Digital":
                        self.digitalWrite(pin, value)
                    
s = Server(host=HOST, port=PORT, deviceData=deviceData)
s.connectSocket()
while True:
    s.handleCommands(s.reciveCommands())
    