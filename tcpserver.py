#!/usr/bin/env python3.10

import socket
from socket import AF_INET, SOCK_DGRAM
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
    
    serverSocket = socket.socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', int(listening_port)))
    
    # TODO: only one client at a time
    header_len = 0b0101
    server_isn = 0
    handshake_complete = False

    # receive packets
    while True:
        if (handshake_complete):

            # initialized ack and seq nums for stop n wait protocol
            ack_num = 0
            seq_num = 1

            # write to file
            with open(file_name, "wb") as f:
                flag = 0
                while True:

                    # receive packet
                    bytes_read = serverSocket.recv(MAX_SEGMENT_SIZE + 20)
                    header = bytes_read[:20]
                    data = bytes_read[20:]
                    rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum = unpack_header(header)
                    if(is_fin):
                        # received FIN request
                        # send ACK
                        flag_and_len_as_int = set_flags(header_len, True, False, False)
                        ack_packet = struct.pack("h h i i h h h h", int(listening_port), int(port_for_acks),
                                rec_ack, rec_seq, flag_and_len_as_int, 0,
                                0, 0)
                        # send ACK
                        serverSocket.sendto(ack_packet, (address_for_acks, int(port_for_acks)))

                        # send FIN
                        while True:
                            flag_and_len_as_int = set_flags(header_len, False, False, True)
                            # switch seq and ack num
                            fin_packet = struct.pack("h h i i h h h h", int(listening_port), int(port_for_acks),
                                    rec_seq, rec_ack, flag_and_len_as_int, 0,
                                    0, 0)
                            serverSocket.sendto(fin_packet, (address_for_acks, int(port_for_acks)))

                            # receive ack
                            serverSocket.settimeout(1)
                            try:
                                message = serverSocket.recv(20) # ERROR: blocking here
                                rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum = unpack_header(message)
                                if (not is_ack):
                                    print('Error: final ACK not received') 
                                    print('Resending FIN request')
                                    fin_packet = struct.pack("h h i i h h h h", int(listening_port), int(port_for_acks),
                                    rec_seq, rec_ack, flag_and_len_as_int, 0,
                                    0, 0)
                                elif(is_ack):
                                    break
                            except socket.timeout:
                                # never received final ACK
                                print('Error: final ACK not received') 
                                print('Resending FIN request')
                                fin_packet = struct.pack("h h i i h h h h", int(listening_port), int(port_for_acks),
                                    rec_seq, rec_ack, flag_and_len_as_int, 0,
                                    0, 0)

                        f.close()
                        handshake_complete = False
                        serverSocket.settimeout(None)
                        break
                    else:
                        # file data received
                        unpacked = struct.unpack('h h i i h h h h', header)
                        # send ACK
                        # switch ack and seq nums for stop and wait implementation
                        flag_and_len_as_int = set_flags(header_len, True, False, False)
                        ack_packet = struct.pack("h h i i h h h h", int(listening_port), int(port_for_acks),
                                rec_ack, rec_seq, flag_and_len_as_int, 0,
                                0, 0)
                        # send ACK
                        serverSocket.sendto(ack_packet, (address_for_acks, int(port_for_acks)))
                        
                        # write to file
                        f.write(data)
        
        # 3 way handshake
        else:
            message, clientAddress = serverSocket.recvfrom(20)
            rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum = unpack_header(message)

            # if SYN segment, send SYNACK segment
            if(is_syn):
                ack_num = rec_seq + 1
                flag_and_len_as_int = set_flags(header_len, is_ack, is_syn, is_fin)
                SYNACK_segment = struct.pack("h h i i h h h h", int(listening_port), int(port_for_acks),
                                server_isn, ack_num, flag_and_len_as_int, 0,
                                0, 0)
                serverSocket.sendto(SYNACK_segment, (address_for_acks, int(port_for_acks)))

                # complete handshake
                message, clientAddress = serverSocket.recvfrom(20)
                unpacked = struct.unpack('h h i i h h h h', message)
                handshake_complete = True
        
            else:
                print('Error: three-way handshake must be setup first')
                unpacked = struct.unpack('h h i i h h h h', message)
                rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum = unpack_header(message)
                continue
