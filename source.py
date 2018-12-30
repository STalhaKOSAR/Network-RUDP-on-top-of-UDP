from utils import *
import socket
import time, sys
import sys

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


    def send(self, data,flag = 0):
        packet = make_packet(0, data, flag)
        self.localSocket.send(data)


    def sendFile(self, filename, to):
        start_time = time.time()
        try:
            self.localSocket.connect(to)
        except:
            print("Cannot connect to {}.".format(to), file=sys.stderr)
            sys.exit(-1)

        print("Start to send file: " + filename)

        for data in readFile(filename, chunk_size=DATA_LENGTH):
            self.send(data)


        print("Starting time : ",start_time)

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