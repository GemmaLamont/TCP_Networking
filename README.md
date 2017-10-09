# TCP_Networking
An pair programmed TCP client - channel - receiver networking assignment

Programmed by Gemma Lamont and Alanna Reid

This program emulates a TCP client sending packets to a receiver via a channel to an intended receiver 
using theSend-And-Wait Protocol.

• The sender has two sockets sin and sout.
• The channel has four sockets cs,in, cs,out, cr,in and cr,out.
• The receiver has two sockets rin and rout.

----------       ----------       ----------
| Sender  | <--> | Channel | <--> | Recevier|
----------       ----------       ----------

The max packet length is 512.

=================================================================
Licence
=================================================================

Ideally this program would be released open source on GitHub.com under Apache II licence.
However as this code is considered a part of an assignment it cannot be distributed.
