from utils import *
import socket
import time, sys
import sys
import ntplib
class Source():

    def __init__(self, port=None):
        self.port = port
        try:
            self.localSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if port is not None:
                self.localSocket.bind(('', port))
                self.localSocket.listen()
                print("Socket start at port {}".format(port))
        except socket.error as e:
            print(e)
            sys.exit(-1)


    def sendFile(self, filename, to):
        print("Start to send file: " + filename)
        c = ntplib.NTPClient()     
        response = c.request('time.google.com')
        timer = response.tx_time
        print("First packet send at {}".format(timer))
        try:
            self.localSocket.connect(to)
        except:
            print("Cannot connect to {}.".format(to), file=sys.stderr)
            sys.exit(-1)

        for data in readFile(filename, chunk_size=DATA_LENGTH):
            self.localSocket.send(data)


    def shutDown(self):
        try:
            self.localSocket.close()
        except:
            pass


argv = sys.argv

dest_host = argv[1]
dest_port = int(argv[2])
filename  = argv[3]

Source().sendFile(filename, (dest_host, dest_port))
Source().shutDown