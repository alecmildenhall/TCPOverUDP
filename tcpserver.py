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