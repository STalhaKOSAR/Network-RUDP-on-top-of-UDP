from utils import *
import socket
import time, sys
import random
import threading
import ntplib


nextseq = 0
i = 0
deneme = []
deneme2 = []
class Destination:

    def __init__(self, port=None):
        self.local = port
        self.pkts = []
        # self.nextseq = 0
        self.setup()

    def setup(self):
        try:
            self.localSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if self.local is not None:
                self.localSocket.bind(('', self.local))
                print("Successfully setup socket at {}".format(self.local))
        except socket.error:
            print("Cannot setup the socket.", file=sys.stderr)
            sys.exit(-1)
    
    def saver(self,message):
        global i
        deneme.append(message)
        i += 1

    def writeToFile(self):
        for i in range (0,len(deneme)):
            checkSum, sum, seqnum, flag, data = parse_packet(deneme[i])
            deneme2.append([seqnum,data]) 

        deneme2.sort()
        for i in range (0,len(deneme)):
            deneme[i] =deneme2[i][1]

        with open('saved/' + "input2.txt", 'wb') as fl:
            for data in deneme:
                fl.write(data)

        print("Saved to input2.txt")

    def recv(self):
        global nextseq,deneme
        ACKS = 0
        NACKS = 0

        self.localSocket.settimeout(60) 
        while True:
            try:
                message, address = self.localSocket.recvfrom(MAX_SIZE)
                checkSum, sum, seqnum, flag, data = parse_packet(message)
                self.saver(message)
                # check sum and seqnum
                if checkSum != sum or seqnum != nextseq:
                    ACK = make_ack(nextseq - 1)
                    NACKS += 1
                    self.localSocket.sendto(ACK, address)
                    # print("ACK: {}, NAK: {}.".format(ACKS, NACKS), end='\r')
                else:
                    # ACK
                    ACK = make_ack(nextseq)
                    self.localSocket.sendto(ACK, address)
                    ACKS += 1
                    # print("ACKS: {}, NAK: {}.".format(ACKS, NACKS), end='\r')
                    nextseq = (nextseq + 1) & 0xffff
                    yield data

                    # Last packet received
                    if flag == 2 or data==b'' :
                        c = ntplib.NTPClient()     
                        response = c.request('time.google.com')
                        timer = response.tx_time
                        print("Last packet received at {}".format(timer))
                        break
            
            except socket.timeout:
                print('timeout ? end.')
                break

    def recvFile(self):
        print("waiting for file")
        received = self.recv()
        i = 0
        for data in received:
            i = 1
        
        self.writeToFile()
    


    def shutDown(self):
        try:
            self.localSocket.close()
        except:
            pass




argv = sys.argv


port = int(argv[1])
port2 = int(argv[2])

destination = Destination(port)
destination2 = Destination(port2)

threads = []

try:
    thread1 = threading.Thread(target=destination.recvFile)
    thread2 = threading.Thread(target=destination2.recvFile)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

except:
    print ("Error: unable to start thread")

destination.shutDown()
destination2.shutDown()

    

