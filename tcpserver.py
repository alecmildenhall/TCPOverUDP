#!/usr/bin/env python3.10

from socket import *
import sys

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
    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        modifiedMessage = message.decode()
        print('Handled client: ' + str(clientAddress)+ ' who sent: ' +
              message.decode())
        
    # receiver sends acknowledgments directly to the sender

    # the server receives data on the listening_port, writes it to the file file 
    # sends ACKs to ip_address_for_acks, port port_for_acks
