from utils import *
import socket
import time, sys
import random



class SendToDest:
    def __init__(self, port=None, window_size=10):
        self.port = port
        self.window_size = window_size
        self.pkts = []
        self.nextseq = 0
        self.timer = 0.0
        self.setup()

    def setup(self):
        try:
            self.localSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if self.port is not None:
                self.localSocket.bind(('', self.port))
                print("Successfully setup socket at {}".format(self.port))
        except socket.error:
            print("Cannot setup the socket.", file=sys.stderr)
            sys.exit(-1)

    TIMEOUT = 0.2

    def sendAll(self, sendTo):
        for pkt in self.pkts:
            self.localSocket.sendto(pkt, sendTo)

    def sendPkt(self, pkt, sendTo):
        self.pkts.append(pkt)
        self.localSocket.sendto(pkt, sendTo)
        self.nextseq = (self.nextseq + 1) & 0xffff
        if len(self.pkts) == 1:
            self.start_timer()

    def start_timer(self):
        self.timer = time.time()

    def send(self, data, sendTo, flag=0):
        unacked = len(self.pkts)
        packet = make_packet(self.nextseq, data, flag)
        oldest_unack = (self.nextseq - unacked) & 0xffff
        # fall back to fixed timeout value
        self.localSocket.settimeout(0.1)
        lastsent = False

        if flag == 2 and unacked < self.window_size:
            self.sendPkt(packet)
            lastsent = True

        while unacked >= self.window_size or (flag == 2 and unacked > 0):
            try:
                pkt, address = self.localSocket.recvfrom(MAX_SIZE)

            except socket.timeout:
                # resend all pkts
                if time.time() - self.timer < self.TIMEOUT:
                    self.start_timer()
                    self.sendAll(sendTo)
                    print("go back n, resend all")
            else:
                csum, rsum, seq, _, _ = parse_packet(pkt)

                # not corrupted
                if csum == rsum:
                    # cumulative acknowledgement
                    cum_acks = seq - oldest_unack + 1
                    if cum_acks < 0: # seqnum restarts from zero
                        cum_acks = seq + 1 + 0xffff - oldest_unack + 1
                    self.pkts = self.pkts[cum_acks:]
                    #print("seq: {}, oldest: {} cum ACK {}".format(seq, oldest_unack, cum_acks))
                    unacked -= cum_acks
                    oldest_unack = (oldest_unack + cum_acks) & 0xffff

                    if unacked != 0:
                        self.start_timer()

                    if flag == 2 and not lastsent:
                        self.sendPkt(packet, sendTo)
                        lastsent = True


        # ok to send now
        if flag != 2:
            self.sendPkt(packet, sendTo)



class ReceiveFromSource():

    def __init__(self, port=None):
        self.port = port
        try:
            self.localSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if port is not None:
                self.localSocket.bind(('', port))
                print("Successfully setup socket at port {}".format(port))
                self.localSocket.listen()
                print("localSocket starts to listen.")
        except socket.error as e:
            print(e)
            print("Cannot setup the socket.", file=sys.stderr)
            sys.exit(-1)

        self.sent = 0


    def recv(self):
        sender = SendToDest(window_size=10)
        total = 0
        self.receiveSocket.settimeout(.1)
        while True:
            try:
                data = self.receiveSocket.recv(DATA_LENGTH)

                if random.uniform(0,1) < 0.5:
                    sender.send(data,("10.10.5.2",12006))

                else :
                    sender.send(data,("10.10.3.2",12007))

                if not data:
                    break
                yield data
                # last packet, don't wait for timeout

            except socket.timeout:
                print('timeout. end.')
                break

    def recvFile(self):
        try:
            self.receiveSocket, addr = self.localSocket.accept()
        except:
            print("error.", file=sys.stderr)
            sys.exit(-1)
        else:
            received = self.recv()
            with open('saved/' + "input.txt", 'wb') as fl:
                for data in received:
                    fl.write(data)
            self.receiveSocket.close()
            print("\nReceived.")

    def shutDown(self):
        try:
            self.localSocket.close()
        except:
            pass



argv = sys.argv

port = int(argv[1])

broker = ReceiveFromSource(port)

broker.recvFile()

broker.shutDown()