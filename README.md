# README
This program is a simplified version of the Transmission Control Protocol (TCP) that operates over User Datagram Protocol (UDP). 

### Requirements:
- Python version 3.10 (or later)
- import / use socket, sys, struct, os, and errno libraries
- Download newudpl link emulator
- MacOS environment

### How to run program:
1. Set up link emulator
```bash
./newudpl -p 2222:2233 -i 127.0.0.1:6666 -o 127.0.0.1:5555 -vv -L10
```
- this sets up the emulator with 10% packet loss
- 2222 is the receive port
- 2233 is the send port
- 127.0.0.1:6666 is the input host address
- 127.0.0.1:5555 is the output host address

2. Set up the server
```bash
python tcpserver.py output.txt 5555 127.0.0.1 6666
```
- output.txt is the name of the file to write to
- 5555 is the listening port
- 127.0.0.1 is the address for acks
- 6666 is the port for acks

3. Set up the client
```bash
python tcpclient.py file.txt 127.0.0.1 2222 512 6666
```
- file.txt is the file to read data from
- 127.0.0.1 is the address of udpl 
- 2222 is the port number of udpl 
- 512 is the windowsize
- 6666 is the ack port number

### Features:
Three-way handshake implementation, data transmission and reception, FIN request to signal end of transmission, error logging, 20-byte TCP header implementation, sequence number checking, timer for retransmission timeout, handling of command line arguments. See design.md for more.

### Files description:
#### tcpserver.py:
Takes an input of the listening port, the address for acks, the port for acks, and a file name. Recieves a connection from a client and communicates in a 3 way handshake. Receives segments from the client with headers and data from the file which the server writes to a file with the file name given in the command line arguments. When all file data is sent, the server receives a FIN request from the client. When packets are lost and errors occur, errors are logged to the console and packet retransmission occurs. The server uses stop and wait protocol.

#### tcpclient.py
Takes an input of a file name, the address of udpl, the port of udpl, the window size, and the ack port number. The client requests a connection with the server and communicates via a 3 way handshake before sending over packets of windowsize bytes of the file given by the command line arguments to udpl which forwards them to the client. When the client is done transmitting it sends a FIN request to the server. When packets are lost and errors occur, errors are logged to the console and packet retransmission occurs. The client uses stop and wait protocol. 

#### file.txt
This is the file used for testing that is given by client's command line arguments to be sent to the server.

#### README.md
This is the README file included.

#### design.md
Document that describes the program design, functionality, and tradeoffs.

#### screendump.md
File that includes screen dump of a typical client-server interaction.
