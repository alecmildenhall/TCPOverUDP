#!/usr/bin/env python3.10

from socket import *
import sys
import struct

MAX_SEGMENT_SIZE = 576

## Helper Functions ##
def decode_binary(len_header_string):
    rec_len = 20
    is_ack = False
    is_syn = False
    is_fyn = False

    len_header_bin = bin(len_header_string)

    if (int(len_header_bin[-5: -4])):
        is_ack = True
    if (int(len_header_bin[-2: -1])):
        is_syn = True
    if (int(len_header_bin[-1:])):
        is_fyn = True

    return rec_len, is_ack, is_syn, is_fyn

def unpack_segment(message):
    unpacked = struct.unpack('h h i i h h h h', message)
    rec_seq = unpacked[2]
    rec_ack = unpacked[3]
    rec_len, is_ack, is_syn, is_fyn = decode_binary(unpacked[4])
    rec_windowsize = unpacked[5]
    rec_checksum = unpacked[6]

    return rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fyn, rec_windowsize, rec_checksum

def set_flags(header_len, is_ack, is_syn, is_fyn):
    ack_flag = 0b010000 if is_ack else 0
    syn_flag = 0b000010 if is_syn else 0
    fyn_flag = 0b000001 if is_fyn else 0

    flag_and_len_as_int = (header_len << 12) | syn_flag | ack_flag | fyn_flag
    return flag_and_len_as_int


if __name__ == "__main__":

    # take command line arguments
    try:
        file_name = sys.argv[1]
        address_of_udpl = sys.argv[2]
        port_number_of_udpl = sys.argv[3]
        windowsize = sys.argv[4]
        ack_port_number = sys.argv[5]

    except:
        print('use: tcpclient <file> <address_of_udpl> ' \
              '<port_number_of_udpl> <windowsize> <ack_port_number>')
        sys.exit()
    
    # creation of client socket
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(('', int(ack_port_number)))

    # client initiates 3 way handshake
    client_isn = 0
    header_len = 0b0101 # 4 bits representing 20 bytes
    flag_and_len_as_int = set_flags(header_len, False, True, False)

    # construct SYN segment
    SYN_segment = struct.pack("h h i i h h h h", int(ack_port_number), int(port_number_of_udpl),
                               client_isn, 0, flag_and_len_as_int, 0,
                               0, 0)

    # send SYN segment
    clientSocket.sendto(SYN_segment,(address_of_udpl, int(port_number_of_udpl)))
    # TODO: should recieve windowsize + MSS?

    # receive SYNACK segment
    serverMessage, serverAddress = clientSocket.recvfrom(2048)
    unpacked = struct.unpack('h h i i h h h h', serverMessage)
    print("SYNACK segment: " + str(unpacked))
    rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fyn, rec_windowsize, rec_checksum = unpack_segment(serverMessage)

    # TODO: allocate buffers and vars for connection

    # finish handshake
    seq_num = rec_ack
    ack_num = rec_seq + 1
    flag_and_len_as_int = set_flags(header_len, True, False, False)
    
    handshake_segment = struct.pack("h h i i h h h h", int(ack_port_number), int(port_number_of_udpl),
                               seq_num, ack_num, flag_and_len_as_int, 0,
                               0, 0)
    clientSocket.sendto(handshake_segment,(address_of_udpl, int(port_number_of_udpl)))

    # TODO: divide up file into packets
    while True:
        # send transmission
        pass

    clientSocket.close()

    # sender sends packets to the emulator, which forwards them to the receiver

    # reads data from the specified file, sends it to the emulator's address and port, 
    # and receives acknowledgments on the ack_port_number
    # window size is measured in bytes and can be set to any reasonable default value

    # randomly chose initial seq # (see page 233)