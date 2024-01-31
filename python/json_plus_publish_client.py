#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 21:06:14 2024

@author: john
"""

import socket
import struct
import time

import json_plus

HOST = "192.168.50.96"  # The server's hostname or IP address
PORT = 30010  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    for _ in range(5):
        metadata = {'duration': 5, 'rate': 10e6, 'freq': 101e6, 'gain': 60}
        payload = struct.pack('HHHH', 0x11, 0x22, 0x33, 0x44)
        
        pkt = json_plus.encode(metadata, payload)

        print(' '.join('%02x'%b for b in pkt))

        s.sendall(pkt)

        time.sleep(5)        

    for _ in range(5):
        metadata = {'temp_degF': 90.0, 'voltage': 12.0}
        payload = bytes('''Three Rings for the Elven-kings under the sky,
Seven for the Dwarf-lords in their halls of stone,
Nine for Mortal Men, doomed to die,
One for the Dark Lord on his dark throne
In the Land of Mordor where the Shadows lie.
One Ring to rule them all, One Ring to find them,
One Ring to bring them all and in the darkness bind them.
In the Land of Mordor where the Shadows lie.''', 'utf-8')
        
        pkt = json_plus.encode(metadata, payload)

        print(' '.join('%02x'%b for b in pkt))

        s.sendall(pkt)

        time.sleep(5)        

        