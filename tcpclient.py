#!/usr/bin/env python3.10

from socket import *
import sys

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
    message = "test"
    clientSocket.sendto(message.encode(),(address_of_udpl, int(port_number_of_udpl)))
    serverMessage, serverAddress = clientSocket.recvfrom(2048)
    print('Receive from server: ' + serverMessage.decode())
    clientSocket.close()
    # sender sends packets to the emulator, which forwards them to the receiver

    # reads data from the specified file, sends it to the emulator's address and port, 
    # and receives acknowledgments on the ack_port_number
    # window size is measured in bytes and can be set to any reasonable default value
