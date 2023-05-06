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
        listening_port = sys.argv[2]
        address_for_acks = sys.argv[3]
        port_for_acks = sys.argv[4]

    except:
        print('use: tcpserver <file> <listening_port> ' \
              '<address_for_acks> <port_for_acks>')
        sys.exit()
    
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', int(listening_port)))
    # TODO: only one client at a time
    server_isn = 0
    handshake_complete = False
    header_len = 0b0101
    while True:
        # TODO: change size?
        message, clientAddress = serverSocket.recvfrom(2048)
        unpacked = struct.unpack('h h i i h h h h', message)
        print("lvl 1 unpacked (should be SYN): " + str(unpacked))
        # unpacked: (source port, dest port, seq num, ack num,
        #            header len + flags, window, checksum, urgent)
        rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fyn, rec_windowsize, rec_checksum = unpack_segment(message)

        # if SYN segment, send SYNACK segment
        if(is_syn):
            print('SYN segment received')
            server_isn = 0
            ack_num = rec_seq + 1
            flag_and_len_as_int = set_flags(header_len, is_ack, is_syn, is_fyn)
            # TODO: allocate buffers and vars for connection
            SYNACK_segment = struct.pack("h h i i h h h h", int(listening_port), int(port_for_acks),
                               server_isn, ack_num, flag_and_len_as_int, 0,
                               0, 0)
            serverSocket.sendto(SYNACK_segment, (address_for_acks, int(port_for_acks)))
            print('sent SYNACK_segment')

            # complete handshake
            message, clientAddress = serverSocket.recvfrom(2048)
            unpacked = struct.unpack('h h i i h h h h', message)
            print("complete handshake segment: " + str(unpacked))
            handshake_complete = True
        
        elif(handshake_complete):
            while True:
                # receive transmission of packets
                pass
        else:
            print('Error: three-way handshake must be setup first')



        
    # receiver sends acknowledgments directly to the sender

    # the server receives data on the listening_port, writes it to the file file 
    # sends ACKs to ip_address_for_acks, port port_for_acks

    # randomly chose initial seq # (see page 233)
