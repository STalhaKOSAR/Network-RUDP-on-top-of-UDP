from utils import *
import socket
import time, sys
import random

class Destination:

    def __init__(self, port=None):
        self.local = port
        self.pkts = []
        self.nextseq = 0
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

    def recv(self):
        acks = 0
        nacs = 0

        self.localSocket.settimeout(60) 
        while True:
            try:
                message, address = self.localSocket.recvfrom(MAX_SIZE)

                csum, rsum, seqnum, flag, data = parse_packet(message)

                # check sum and seqnum
                if csum != rsum or seqnum != self.nextseq:
                    ACK = make_ack(self.nextseq - 1)
                    nacs += 1
                    self.localSocket.sendto(ACK, address)
                    print("acks: {}, NAK: {}.".format(acks, nacs), end='\r')
                else:
                    # ack
                    ACK = make_ack(self.nextseq)
                    self.localSocket.sendto(ACK, address)
                    acks += 1
                    print("acks: {}, NAK: {}.".format(acks, nacs), end='\r')
                    self.nextseq = (self.nextseq + 1) & 0xffff
                    yield data
                    # last packet, don't wait for more packets
                    if flag == 2 or data==b'' :
                        print("\n last packet received.")
                        break
            except socket.timeout:
                print('timeout ? end.')
                break

    def recvFile(self):
        print("waiting for file")

        received = self.recv()

        with open('saved/' + "input2.txt", 'wb') as dl:
            for data in received:
                dl.write(data)

        print("Received: {}.".format("input2.txt"))


    def teardown(self):
        try:
            self.localSocket.close()
        except:
            pass




argv = sys.argv


port = int(argv[1])

destination = None
destination = Destination(port)

destination.recvFile()

destination.teardown()

    

