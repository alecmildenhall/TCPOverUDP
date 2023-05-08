### Emulator screen dump
```bash
./newudpl -p 2222:2233 -i 127.0.0.1:6666 -o 127.0.0.1:5555 -vv -L50

Network emulator with UDP link
 Copyright (c) 2021 by Columbia University; all rights reserved

Link established:
  localhost(127.0.0.1)/6666 ->
          Alecs-MBP.fios-router.home(192.168.1.239)/2222
  /2233 ->
          localhost(127.0.0.1)/5555

emulating speed  : 1000 kb/s
delay            : 0.000000 sec
Ethernet         : 10 Mb/s
Queue buffersize : 8192 bytes

error rate
    Random packet loss: 50%
    Bit error         : 0 (1/100000 per bit)
    Out of order      : 0%
    Jitter            : 0% of delay

received: recv counter: 0  size: 20 bytes
  this is the first packet:
send    : send counter: 0  size: 20 bytes
received: recv counter: 20  size: 20 bytes
Packet loss:
  discarded packet: send counter: 20  size: 20 bytes
received: recv counter: 40  size: 55 bytes
send    : send counter: 20  size: 55 bytes
received: recv counter: 95  size: 55 bytes
Packet loss:
  discarded packet: send counter: 75  size: 55 bytes
received: recv counter: 150  size: 55 bytes
Packet loss:
  discarded packet: send counter: 75  size: 55 bytes
received: recv counter: 205  size: 55 bytes
Packet loss:
  discarded packet: send counter: 75  size: 55 bytes
received: recv counter: 260  size: 55 bytes
Packet loss:
  discarded packet: send counter: 75  size: 55 bytes
received: recv counter: 315  size: 55 bytes
send    : send counter: 75  size: 55 bytes
received: recv counter: 370  size: 20 bytes
send    : send counter: 130  size: 20 bytes
received: recv counter: 390  size: 20 bytes
Packet loss:
  discarded packet: send counter: 150  size: 20 bytes
received: recv counter: 410  size: 20 bytes
received: recv counter: 430  size: 20 bytes
send    : send counter: 150  size: 20 bytes
Packet loss:
  discarded packet: send counter: 170  size: 20 bytes
```

### Server screen dump
```bash
python tcpserver.py output.txt 5555 127.0.0.1 6666
Error: final ACK not received
Resending FIN request
```

### Client screen dump
```bash
python tcpclient.py file.txt 127.0.0.1 2222 512 6666
Error: timed out before ACK received
Retransmitting packet
Error: timed out before ACK received
Retransmitting packet
Error: timed out before ACK received
Retransmitting packet
Error: timed out before ACK received
Retransmitting packet
Error: timed out before ACK received
Retransmitting packet
Error: ACK is lost, resending final acknowledgment
```