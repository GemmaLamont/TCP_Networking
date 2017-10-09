#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import socket
import select
import jsonpickle
import Packet
import os.path


def argument_reader():
    """Reads in all the needed arguments from the command"""

    arguments = sys.argv[1:]
    Sin = int(arguments[0])
    Sout = int(arguments[1])
    Csin = int(arguments[2])
    file_name = str(arguments[3])
    return (Sin, Sout, Csin, file_name)


def argument_checker(Sin, Sout):
    """Reads the 2 arguments in from the command line and checks if they're of the correct format"""

    if not (Sin < 64000 and Sin > 1024):
        print('ERROR: Ports of wrong size')
        return False
    if not (Sout < 64000 and Sout > 1024):
        print('ERROR: Ports of wrong size')
        return False
    return True


def packet_maker(seq, message):
    """Creates a packet with sequence number seq
    and of data = message"""

    packet = Packet.Packet(0, seq, len(message), message)
    return packet


def main():
    (Sin, Sout, Csin, file_name) = argument_reader()
    arguments = argument_checker(Sin, Sout)

    if arguments:

        SinSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SoutSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Define all separate sever addresses (IP, Port)

        SinSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        SoutSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_address_Sin = ('127.0.0.1', Sin)
        server_address_Sout = ('127.0.0.1', Sout)

        # Bind all four channel sockets

        SinSocket.bind(server_address_Sin)
        SoutSocket.bind(server_address_Sout)

        # Connecting to channel Sin socket

        SinSocket.listen(1)
        while True:
            try:
                (connection_Sin, address) = SinSocket.accept()
                print('Accepted Sin')
                break
            except OSError as e:
                print('Could not accept from Sin')

        while True:
            try:
                SoutSocket.connect(('127.0.0.1', Csin))
                print('Connected to Csin')
                break
            except OSError as e:
                print('Could not connect to Csin')

        if os.path.isfile(file_name):
            file = open(file_name, 'r')
        else:
            arguments = False
            print('Cannot find file')

    next = 0
    initial_packets = 0
    resent_packets = 0
    while arguments:
        message = file.read(512)
        if len(message) == 0:
            arguments = False
        packet = packet_maker(next, message)
        packet = jsonpickle.encode(packet).encode()

        received = False

        initial_packets += 1
        while not received:
            (ready_to_read, ready_to_write, in_error) = \
                select.select([connection_Sin], [], [], 1.0)

            SoutSocket.sendall(packet)
            resent_packets += 1
            for i in ready_to_read:
                if i == connection_Sin:
                    Sin_packet = connection_Sin.recv(1024)
                    decoded_packet = Sin_packet.decode()
                    try:
                        rcvd = jsonpickle.decode(decoded_packet)
                    except:
                        print('Packet received was unable to be depickled; aborting program')
                        break

                    # Checks magnico, if incorrect goes back to start of loop

                    if rcvd.magnico == 0x497E:
                        if rcvd.data_len == 0 and rcvd.type == 1:
                            if rcvd.seqno == next:
                                received = True
                                next = 1 - next
                    else:
                        print('Packet had Wrong Magnico')
    file.close()
    SinSocket.close()
    SoutSocket.close()
    print(initial_packets + resent_packets)


if __name__ == '__main__':
    main()