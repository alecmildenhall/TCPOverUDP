### Overall program design + "how it works"
The program operates a simplified version of TCP over UDP. The server and client start from the tcpserver.py and tcpclient.py files respectively and udpl acts as a proxy between them. The client and server initiate a 3 way handshake and then the client sends the server packets of windowsize bytes of the specified file with TCP headers for the server to download. This is done using stop and wait protocol. When the client is finished sending all file packets, the client sends a FIN request and the connection is shut down. The client waits 30 seconds before closing. When packets are lost and errors occur, errors are logged to the console and packet retransmission occurs. 

### Design tradeoffs
I chose to use stop and wait protocol for data transmission and retransmission. This means the sequence and numbers are simplified, alternating between 1 and 0, and packets are never sent out of order. If timeout occurs, packets are retransmitted. The drawback slower communication and no pipelining. 