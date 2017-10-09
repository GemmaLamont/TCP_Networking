#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import socket
import select
import jsonpickle
import random


def argument_reader():
    """Reads the 7 arguments in from the command line and checks if they're of the correct format"""

    arguments = sys.argv[1:]
    Csin = int(arguments[0])
    Csout = int(arguments[1])
    Crin = int(arguments[2])
    Crout = int(arguments[3])
    Sin = int(arguments[4])
    Rin = int(arguments[5])
    precision_value = float(arguments[6])
    return (
        Csin,
        Csout,
        Crin,
        Crout,
        Sin,
        Rin,
        precision_value,
    )


def argument_checker(
        Csin,
        Csout,
        Crin,
        Crout,
        Sin,
        Rin,
        precision_value,
):
    """"Checks the arguments to be of correct form"""

    if not (Csin < 64000 and Csin > 1024):
        print('ERROR: Cin of wrong size')
        return False

    if not (Csout < 64000 and Csout > 1024):
        print('ERROR: Csout of wrong size')
        return False

    if not (Crin < 64000 and Crin > 1024):
        print('ERROR: Crin of wrong size')
        return False

    if not (Crout < 64000 and Crout > 1024):
        print('ERROR: Crout of wrong size')
        return False

    if Sin == Rin:
        print('ERROR: Port numbers are the same')
        return False

    if not (precision_value < 1 and precision_value >= 0):
        print('ERROR: precision value of wrong size')
        return False

    return True


def packet_checker(packet):
    """Creates a packet with sequence number seq
    and of data = message"""

    if packet.magnico != 0x497E:
        return False
    return True


def packet_loss(P):
    """Adds a uniformly distributed packet loss, returns True if packet to be dropped"""

    u = random.uniform(0, 1)
    if u < P:
        return True
    return False


def add_bit_errors(packet):
    """Adds a bit error over a uniformly distributed"""

    v = random.uniform(0, 1)
    if v < 0.1:
        data_len_increment = random.randint(1, 10)
        packet.data_len += data_len_increment
    return packet


def main():
    (
        Csin,
        Csout,
        Crin,
        Crout,
        Sin,
        Rin,
        precision_value,
    ) = argument_reader()
    arguments = argument_checker(
        Csin,
        Csout,
        Crin,
        Crout,
        Sin,
        Rin,
        precision_value,
    )

    # gives random a seed

    random.seed

    # create all four channel sockets

    if arguments:
        CsinSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CsoutSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CrinSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        CroutSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Define all separate sever addresses (IP, Port)

        CsinSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        CsoutSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                               1)
        CrinSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        CroutSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                               1)

        server_address_Csin = ('127.0.0.1', Csin)
        server_address_Csout = ('127.0.0.1', Csout)
        server_address_Crin = ('127.0.0.1', Crin)
        server_address_Crout = ('127.0.0.1', Crout)

        # Bind all four channel sockets

        CsinSocket.bind(server_address_Csin)
        CsoutSocket.bind(server_address_Csout)
        CrinSocket.bind(server_address_Crin)
        CroutSocket.bind(server_address_Crout)
        while True:
            try:
                CsoutSocket.connect(('127.0.0.1', Sin))
                print('Connected Csout socket')
                break
            except OSError as e:
                print('Not connected to Csout')
        while True:
            try:
                CroutSocket.connect(('127.0.0.1', Rin))
                print('Connected Crout socket')
                break
            except OSError as e:
                print('Not connected to Crout')

        CsinSocket.listen()
        while True:
            try:
                (connection_Csin, addr) = CsinSocket.accept()
                print('Connected to Csin')
                break
            except OSError as e:
                print('Not connected to Csin')
        CrinSocket.listen()
        while True:
            try:
                (connection_Crin, addr) = CrinSocket.accept()
                print
                'Connected to Crin'
                break
            except OSError as e:
                print('Not connected to Crin')

        # Wait for connection

        true = True
        while true:
            (ready_to_read, ready_to_write, in_error) = \
                select.select([connection_Crin, connection_Csin], [],
                              [])
            for i in ready_to_read:
                if i == connection_Csin:
                    Csin_packet = connection_Csin.recv(1024)

                    # decode the packet twice once from bytes and then from jsonpickle

                    decoded_packet = Csin_packet.decode()
                    try:
                        rcvd_packet = jsonpickle.decode(decoded_packet)
                    except:
                        print('Packet received was unable to be depickled; aborting program')
                        true = False
                        break

                    # checks the magicno

                    if packet_checker(rcvd_packet):

                        # checks to see if it should drop a packet

                        if not packet_loss(precision_value):
                            add_bit_errors(rcvd_packet)

                            # encodes the packet and sends it to the receiver

                            rcvd_packet_pickled = \
                                jsonpickle.encode(rcvd_packet).encode()
                            CroutSocket.sendall(rcvd_packet_pickled)
                        else:
                            print('Packet dropped')
                    else:
                        print('Wrong Magnico')
                elif i == connection_Crin:

                    Crin_packet = connection_Crin.recv(1024)

                    # decode the packet once from bytes and then from json pickle

                    decoded_packet = Crin_packet.decode()
                    try:
                        rcvd_packet = jsonpickle.decode(decoded_packet)
                    except:
                        print('Packet received was unable to be depickled; aborting program')
                        true = False
                        break

                    # check the magicno

                    if packet_checker(rcvd_packet):

                        # checks to see if it should drop the packet

                        if not packet_loss(precision_value):
                            add_bit_errors(rcvd_packet)

                            # encodes the packet again and then sends it to the sender

                            rcvd_packet_pickled = \
                                jsonpickle.encode(rcvd_packet).encode()
                            CsoutSocket.sendall(rcvd_packet_pickled)
                        else:
                            print('Packet dropped')
                    else:
                        print('Wrong Magnico')

        CrinSocket.close()
        CroutSocket.close()
        CsinSocket.close()
        CsoutSocket.close()


if __name__ == '__main__':
    main()

