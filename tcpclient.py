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
        address_of_udpl = sys.argv[2]
        port_number_of_udpl = sys.argv[3]
        windowsize = sys.argv[4]
        ack_port_number = sys.argv[5]

    except:
        print('use: tcpclient <file> <address_of_udpl> ' \
              '<port_number_of_udpl> <windowsize> <ack_port_number>')
        sys.exit()

    if (int(windowsize) > MAX_SEGMENT_SIZE):
        print("Error: windowsize larger than maximum window size of " + str(MAX_SEGMENT_SIZE))
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

    # receive SYNACK segment
    serverMessage, serverAddress = clientSocket.recvfrom(20)
    unpacked = struct.unpack('h h i i h h h h', serverMessage)
    print("SYNACK received: " + str(unpacked))
    rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum = unpack_header(serverMessage)

    # TODO: allocate buffers and vars for connection

    # finish handshake
    seq_num = rec_ack
    ack_num = rec_seq + 1
    flag_and_len_as_int = set_flags(header_len, True, False, False)
    
    handshake_segment = struct.pack("h h i i h h h h", int(ack_port_number), int(port_number_of_udpl),
                               seq_num, ack_num, flag_and_len_as_int, 0,
                               0, 0)
    clientSocket.sendto(handshake_segment,(address_of_udpl, int(port_number_of_udpl)))

    # send file packets

    # check file exists
    path = os.getcwd() + '/'
    file_path = path + '/' + file_name
    if (not os.path.isfile(file_path)):
        print('Error: file does not exist')
        sys.exit()
        
    #file_size = os.path.getsize(file_path)
    #num_packets = file_size / int(windowsize)
    #print('num packets before: ' + str(num_packets))
    #if (file_size % int(windowsize) != 0 or file_size < int(windowsize)):
    #    num_packets = int(num_packets + 1)
    #print('file size: ' + str(file_size))
    #print('num_packets: ' + str(num_packets))
    
    # transmission
    packets_sent = 0
    with open(file_path, "rb") as f:
        while True:
            bytes_read = f.read(int(windowsize))

            # end of file
            if len(bytes_read) == 0:
                break

            # send packet
            format = "h h i i h h h h " + str(len(bytes_read)) + "s"
            flag_and_len_as_int = set_flags(header_len, False, False, False)
            packet = struct.pack(format, int(ack_port_number), int(port_number_of_udpl),
                               seq_num, ack_num, flag_and_len_as_int, 0,
                               0, 0, bytes_read) 
            clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))


    # send FIN request
    flag_and_len_as_int = set_flags(header_len, False, False, True)
    packet = struct.pack("h h i i h h h h", int(ack_port_number), int(port_number_of_udpl),
                               seq_num, ack_num, flag_and_len_as_int, 0,
                               0, 0) 
    clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))
    clientSocket.close()

    # sender sends packets to the emulator, which forwards them to the receiver

    # reads data from the specified file, sends it to the emulator's address and port, 
    # and receives acknowledgments on the ack_port_number
    # window size is measured in bytes and can be set to any reasonable default value

    # randomly chose initial seq # (see page 233)