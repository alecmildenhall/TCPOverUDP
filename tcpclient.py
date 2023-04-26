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
