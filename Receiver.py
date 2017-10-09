#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import socket
import select
import jsonpickle
import Packet
import os.path


def packet_maker(seq, message):
    """Creates a packet with sequence number seq
    and of data = message"""

    packet = Packet.Packet(1, seq, len(message), message)
    return packet


def argument_reader():
    """"Reads in all the required arguments from command"""

    arguments = sys.argv[1:]
    Rin = int(arguments[0])
    Rout = int(arguments[1])
    Crin = int(arguments[2])
    file_name = str(arguments[3])
    return (Rin, Rout, Crin, file_name)


def argument_checker(Rin, Rout):
    """Reads the 2 arguments in from the command line and checks if they're of the correct format"""

    if not (Rin < 64000 and Rin > 1024):
        print('ERROR: Ports of wrong size')
        return False
    if not (Rout < 64000 and Rout > 1024):
        print('ERROR: Ports of wrong size')
        return False
    return True


def main():
    (Rin, Rout, Crin, file_name) = argument_reader()
    arguments = argument_checker(Rin, Rout)

    if arguments:

        RinSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        RoutSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Define all separate sever addresses (IP, Port)

        RinSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        RoutSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_address_Rin = ('127.0.0.1', Rin)
        server_address_Rout = ('127.0.0.1', Rout)

        # Bind all four channel sockets

        RinSocket.bind(server_address_Rin)
        RoutSocket.bind(server_address_Rout)
        RinSocket.listen(1)
        while True:
            try:
                (connection_Rin, address) = RinSocket.accept()
                break
            except OSError as e:
                print('Could not accept from Rin socket')
        while True:
            try:
                RoutSocket.connect(('127.0.0.1', Crin))
                print
                'Connected Rout socket'
                break
            except OSError as e:
                print('Could not connect to Rout socket')

        # Open file to write to, if already exists, abort!

        if os.path.isfile(file_name):
            arguments = False
        else:
            file = open(file_name, 'w+')

    expected = 0
    while arguments:
        (ready_to_read, ready_to_write, in_error) = \
            select.select([connection_Rin], [], [])
        for i in ready_to_read:
            if i == connection_Rin:

                # this checks if the sender has anything to send if so this must not be an empty packet

                Rin_packet = connection_Rin.recv(1024)  # CHECK WHAT THE NUMBER MEANS how many bytes we get =)
                decoded_packet = Rin_packet.decode()
                try:
                    rcvd = jsonpickle.decode(decoded_packet)
                except:
                    print('Packet received was unable to be depickled; aborting program')
                    arguments = False
                    break

                # Checks magnico, if incorrect goes back to start of loop

                if rcvd.magnico == 0x497E and rcvd.type == 0:  # and rcvd.check_for_bit_errors():
                    if rcvd.seqno == expected:
                        if rcvd.check_checksum():
                            expected = 1 - expected

                        if rcvd.data_len > 0:
                            file.write(rcvd.data)
                    if rcvd.check_for_bit_errors():
                        ack_packet = packet_maker(rcvd.seqno, '')
                        ack_packet_pickled = \
                            jsonpickle.encode(ack_packet).encode()
                        RoutSocket.sendall(ack_packet_pickled)
                    else:
                        seqno = expected
                        if rcvd.check_checksum():
                            seqno = 1 - seqno
                        ack_packet = packet_maker(seqno, '')
                        ack_packet_pickled = \
                            jsonpickle.encode(ack_packet).encode()
                        RoutSocket.sendall(ack_packet_pickled)

                    if rcvd.data_len == 0:
                        arguments = False
    file.close()
    RinSocket.close()
    RoutSocket.close()


if __name__ == '__main__':
    main()

