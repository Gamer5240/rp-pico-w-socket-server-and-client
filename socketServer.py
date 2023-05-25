import socket
import threading
import json

HOST = socket.gethostbyname(socket.gethostname()) #grabs your ip address
PORT = 5050

FORMAT = "utf-8"
HEADER = 64

class SocketServer():
    def __init__(self, host=socket.gethostbyname(socket.gethostname()), port=5050, numberOfClients=1):
        self.host = host
        self.port = port
        self.s = ""
        self.numberOfClients = numberOfClients
        self.clients = {}
        self.browserData = {}
    
    '''def getColorPins(self):
        colorPinsData = {}
        for name, data in self.clients.items():
            colorPinsData[name] = data[1]
        return colorPinsData'''
    
    def startSocketServer(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        self.s.listen(self.numberOfClients)

    def handleClientConnection(self):
        while True:
            conn, addr = self.s.accept()
            data = json.loads(conn.recv(1024).decode('utf-8'))
            print(data)
            self.browserData[data["name"]] = data["options"]
            self.clients[data["name"]] = [conn, addr]

    def sendCommand(self, device=None, command=None):
        print("sending command")
        command = json.dumps(command).encode(FORMAT)
        commandLength = len(command)
        sendLength = str(commandLength).encode(FORMAT)
        sendLength += b" " * (HEADER - len(sendLength))
        self.clients[device][0].send(sendLength)
        self.clients[device][0].send(command)
        print(command)
        print("command sent")
        
    def startClientHandeling(self, thread):
        thread.start()
        
    def handleClientConnectionThread(self):
        t1 = threading.Thread(target = self.handleClientConnection, args = ())
        self.startClientHandeling(t1)

if __name__ == "__main__":
    s = SocketServer(host=HOST, port=PORT)
    s.startSocketServer()
    s.handleClientConnectionThread()
    
    while True:
        device = "rp2"
        value1 = int(input("Enter a value \n"))
        value2 = int(input("Enter a value \n"))
        pin = "LED"
        mode = "pwm"
        cmd = [{"pin": 14, "value": value1, "mode": mode},{"pin": 15, "value": value2, "mode": "pwm"}]
        s.sendCommand("rp2", cmd) #command example: [{"pin": pin, "value": value1, "mode": mode},{"pin": 15, "value": value2, "mode": "pwm"}]