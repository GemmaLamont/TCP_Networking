#!/usr/bin/python
# -*- coding: utf-8 -*-
import binascii


class Packet:
    def __init__(
            self,
            type,
            seqno,
            data_len,
            data,
    ):
        self.magnico = 0x497E
        self.type = type
        self.seqno = seqno
        self.data_len = data_len
        self.data = data
        self.checksum = binascii.crc32(self.data.encode())

    def magnico_check(self):
        """Checks if the magnico received is of hexadecimal value 0x497E"""

        if self.magnico == 0x497E:
            return True
        else:
            print('ERROR: magnico is not of correct value')

    def type_distinguisher(self):
        """Distinguishes the two available types: dataPacket and acknowledgementPacket"""

        if self.type == 0:
            return 'dataPacket'
        if self.type == 1:
            return 'acknowledgementPacket'
        return None

    def check_acknowledgement_packet(self):
        """Checks the length of an acknowledgement packet is zero"""

        if self.dataLen != 0:
            print('ERROR: data length of acknowledgement packet is incorrect')

    def check_dataLen(self):
        """Checks the data len is small enough and is of given length"""

        if self.dataLen > 512 or self.dataLen < 0:
            print('Error: Data length out of range')
        if self.dataLen != len(self.data):
            print('ERROR: Data length not equal to actual length of data')

    def check_for_bit_errors(self):
        if self.data_len != len(self.data):
            return False
        return True

    def check_checksum(self):
        """Checks the checksum of the data is equal to the given one"""

        bytes = self.data.encode()
        return self.checksum == binascii.crc32(bytes)



