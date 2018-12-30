
"""
packet utilities

packet specification:
    1. checksum  (1 bytes)
    2. seqnum    (2 bytes) reserved 2 bytes
    3. flag      (1 bytes)  # first packet 0, packet 1, last packet 2
    4. data      (_ bytes) # at most (MAX_SIZE - 4) bytes
A single packet will not exceed MAX_SIZE bytes.
"""
MAX_SIZE = 1000
DATA_LENGTH = MAX_SIZE - 4

SEQ_MAX = 0xffff


def parse_packet(data):
    """
    Parse a packet from at most MAX_SIZE bytes data.
    """
    checked_sum = checksum(data[1:])
    received_sum = int.from_bytes(data[:1], byteorder='big')
    seqnum = int.from_bytes(data[1:3], byteorder='big')
    flag = int.from_bytes(data[3:4], byteorder='big')
    data = data[4:]

    return checked_sum, received_sum, seqnum, flag, data


def make_packet(seqnum, data, flag=0):
    """
    Make a bytes packet from given information
    """
    packet_content = (seqnum.to_bytes(2, byteorder='big') +
                      flag.to_bytes(1, byteorder='big') +
                      data)
    csum = checksum(packet_content)
    return csum.to_bytes(1, byteorder='big') + packet_content


def make_ack(seqnum):
    """
    Make a ack packet
    """
    return make_packet(seqnum, bytes())

def checksum(data):
    """
    Calculate the modular sum of bytes data
    """
    return sum(data) & 0xff


def readFile(filename, chunk_size=256):
    with open(filename, 'rb') as fl:
        while True:
            chunk = fl.read(chunk_size)
            if not chunk:
                break
            yield chunk




