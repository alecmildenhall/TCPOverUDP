#!/usr/bin/env python3.10

from socket import *
import sys
import struct
import os
import errno

MAX_SEGMENT_SIZE = 576

## Helper Functions ##
def decode_binary(len_header_string):
    rec_len = 20
    is_ack = False
    is_syn = False
    is_fin = False

    len_header_bin = bin(len_header_string)

    if (int(len_header_bin[-5: -4])):
        is_ack = True
    if (int(len_header_bin[-2: -1])):
        is_syn = True
    if (int(len_header_bin[-1:])):
        is_fin = True

    return rec_len, is_ack, is_syn, is_fin

def unpack_header(message):
    unpacked = struct.unpack('h h i i h h h h', message)
    rec_seq = unpacked[2]
    rec_ack = unpacked[3]
    rec_len, is_ack, is_syn, is_fin = decode_binary(unpacked[4])
    rec_windowsize = unpacked[5]
    rec_checksum = unpacked[6]

    return rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum


def set_flags(header_len, is_ack, is_syn, is_fin):
    ack_flag = 0b010000 if is_ack else 0
    syn_flag = 0b000010 if is_syn else 0
    fin_flag = 0b000001 if is_fin else 0

    flag_and_len_as_int = (header_len << 12) | syn_flag | ack_flag | fin_flag
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
    header_len = 0b0101
    server_isn = 0
    handshake_complete = False

    # receive packets
    while True:
        print('at start')
        if (handshake_complete):
            print('post handshake')

            # write to file
            with open(file_name, "wb") as f:
                flag = 0
                while True:
                    print('in true')
                    print('before receive')

                    # receive packet
                    bytes_read = serverSocket.recv(MAX_SEGMENT_SIZE + 20)
                    header = bytes_read[:20]
                    print("header: " + str(header))
                    data = bytes_read[20:]
                    print("data: " + str(data))
                    rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum = unpack_header(header)
                    if(is_fin):
                        # received FIN request
                        f.close()
                        print('closed')
                        handshake_complete = False
                        break
                    else:
                        # file data
                        unpacked = struct.unpack('h h i i h h h h', header)
                        print("unpacked: " + str(unpacked))
                        f.write(data)
        
        # 3 way handshake
        else:
            message, clientAddress = serverSocket.recvfrom(20)
            rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum = unpack_header(message)

            # if SYN segment, send SYNACK segment
            if(is_syn):
                print('SYN segment received')
                ack_num = rec_seq + 1
                flag_and_len_as_int = set_flags(header_len, is_ack, is_syn, is_fin)
                # TODO: allocate buffers and vars for connection
                SYNACK_segment = struct.pack("h h i i h h h h", int(listening_port), int(port_for_acks),
                                server_isn, ack_num, flag_and_len_as_int, 0,
                                0, 0)
                serverSocket.sendto(SYNACK_segment, (address_for_acks, int(port_for_acks)))
                print('sent SYNACK_segment')

                # complete handshake
                message, clientAddress = serverSocket.recvfrom(20)
                unpacked = struct.unpack('h h i i h h h h', message)
                print("complete handshake segment: " + str(unpacked))
                handshake_complete = True
        
            else:
                print('Error: three-way handshake must be setup first')
                continue



        
    # receiver sends acknowledgments directly to the sender

    # the server receives data on the listening_port, writes it to the file file 
    # sends ACKs to ip_address_for_acks, port port_for_acks

    # randomly chose initial seq # (see page 233)
