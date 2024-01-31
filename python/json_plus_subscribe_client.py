#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 21:06:14 2024

@author: john
"""

import socket
import struct

HOST = "192.168.50.96"  # The server's hostname or IP address
PORT = 30011  # The port used by the server

TITLE = bytes('JSONPLUS', 'utf-8')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:

        data = s.recv(1024)
        print(' '.join('%02x'%b for b in data))
        
        continue
        
        if data == TITLE:
            print('Received valid title')
            header = s.recv(12)
            if len(header) == 12:
                total_len, json_len, payload_len = struct.unpack('III', header)
                json_bytes = s.recv(json_len)
                payload = s.recv(payload_len)
                if len(json_bytes) == json_len and len(payload) == payload_len:
                    print(f"Received {payload!r}")
            else:
                print('Excess', s.recv(1024))
        else:
            print('Bad title', data)
            print('Excess', s.recv(1024))