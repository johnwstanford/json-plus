#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 21:06:14 2024

@author: john
"""

import socket

import json_plus

HOST = "192.168.50.96"  # The server's hostname or IP address
PORT = 30011  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:

        r = json_plus.try_decode_from_socket(s)
        if r:
            metadata, payload = r
            if metadata == dict() and len(payload) == 0:
                print('Heartbeat')
            if metadata != dict():
                print(metadata)
            if len(payload) > 0:
                if len(payload) < 16:
                    print(' '.join('%02X'%b for b in payload))
                else:
                    print(' '.join('%02X'%b for b in payload[:16]) + ' ...')
            
