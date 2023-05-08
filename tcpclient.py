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
    clientSocket = socket.socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(('', int(ack_port_number)))

    # client initiates 3 way handshake
    client_isn = 0
    header_len = 0b0101 # 4 bits representing 20 bytes
    flag_and_len_as_int = set_flags(header_len, False, True, False)

    # construct SYN segment
    SYN_segment = struct.pack("h h i i h h h h", int(ack_port_number), int(port_number_of_udpl),
                               client_isn, 0, flag_and_len_as_int, 0,
                               0, 0)
    clientSocket.settimeout(1)
    success = False
    while(True):
        # send SYN segment
        clientSocket.sendto(SYN_segment,(address_of_udpl, int(port_number_of_udpl)))

        # receive SYNACK segment
        try:
            serverMessage, serverAddress = clientSocket.recvfrom(20)
        except socket.timeout:
            print('Error: timed out before ACK received')
            print('Restart client to request again')
            continue
        break


    rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum = unpack_header(serverMessage)

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
        
    
    # transmission

    # initialize seq and ack num for stop n wait protocl
    seq_num = 1
    ack_num = 0
    with open(file_path, "rb") as f:
        clientSocket.settimeout(1)
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
            
            # wait for ACK
            clientSocket.settimeout(1)
            while True:
        
                try:
                    ackMessage, serverAddress = clientSocket.recvfrom(20)
                    rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum = unpack_header(ackMessage)
                    if(is_ack):
                        # correct ACK received
                        if(rec_ack == seq_num):
                            # switch seq and ack num
                            seq_num, ack_num = ack_num, seq_num
                            break
                        else:
                            print('Error: incorrect ACK recieved')
                            print("Retransmitting packet")
                            clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))
                    else:
                        print('Error: non ACK packet received')
                        print("Retransmitting packet")
                        clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))
                except socket.timeout:
                    print("Error: timed out before ACK received")
                    print("Retransmitting packet")
                    clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))

    # send FIN request
    flag_and_len_as_int = set_flags(header_len, False, False, True)
    packet = struct.pack("h h i i h h h h", int(ack_port_number), int(port_number_of_udpl),
                               seq_num, ack_num, flag_and_len_as_int, 0,
                               0, 0) 
    clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))

    # wait for ACK
    flag = 0
    while True:
        try:
            ackMessage, serverAddress = clientSocket.recvfrom(20)
            rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum = unpack_header(ackMessage)
            if(is_ack):
                # correct ACK received
                if(rec_ack == seq_num):
                    # switch seq and ack num
                    seq_num, ack_num = ack_num, seq_num
                    flag = 1
                    break
                else:
                    print('Error: incorrect ACK recieved')
                    print("Retransmitting packet")
                    clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))
            else:
                print('Error: non ACK packet received')
                print("Retransmitting packet")
                unpacked = struct.unpack('h h i i h h h h', ackMessage)
                print(unpacked)
                clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))
            
            if (flag):
                break
        except socket.timeout:
            print("Error: timed out before ACK received")
            print("Retransmitting packet")
            clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))


    # wait for FIN request from server
    while True:
        try:
            finMessage, serverAddress = clientSocket.recvfrom(20)
            rec_seq, rec_ack, rec_len, is_ack, is_syn, is_fin, rec_windowsize, rec_checksum = unpack_header(finMessage)
            if(is_fin):
                # correct ACK received
                if(rec_ack == seq_num):
                    # switch seq and ack num
                    seq_num, ack_num = ack_num, seq_num
                    break
                else:
                    print('Error: incorrect packet recieved')
                    print("Retransmitting fin packet")
                    clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))
                    sys.exit()
            else:
                print('Error: non ACK packet received')
                print("Retransmitting fin packet")
                # TODO: error here
                clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))
                sys.exit()
        except socket.timeout:
            print("Error: timed out before ACK received")
            print("Retransmitting packet")
            clientSocket.sendto(packet,(address_of_udpl, int(port_number_of_udpl)))
            sys.exit()


    # send ACK
    while True:
        flag_and_len_as_int = set_flags(header_len, True, False, False)
        ack_packet = struct.pack("h h i i h h h h", int(ack_port_number), int(port_number_of_udpl),
                                rec_ack, rec_seq, flag_and_len_as_int, 0,
                                0, 0)
        clientSocket.sendto(ack_packet,(address_of_udpl, int(port_number_of_udpl)))

        # wait 10 seconds
        # resend final ACK in case gets lost (if recv fin from server)
        clientSocket.settimeout(10)

        try:
            message, serverAddress = clientSocket.recvfrom(20)
            # resend final acknowledgement (ACK is lost)
            print('Error: ACK is lost, resending final acknowledgment')
            clientSocket.sendto(ack_packet,(address_of_udpl, int(port_number_of_udpl)))

        except socket.timeout:
            clientSocket.close()
            break
