#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 21:06:14 2024

@author: john
"""

import json
import socket
import struct
import time

HOST = "192.168.50.96"  # The server's hostname or IP address
PORT = 30010  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    for _ in range(5):
        metadata = {'duration': 5, 'rate': 10e6, 'freq': 101e6, 'gain': 60}
        payload = struct.pack('HHHH', 0x11, 0x22, 0x33, 0x44)
        
        b_json = bytes(json.dumps(metadata), 'utf-8')
        
        json_len = len(b_json)
        pyld_len = len(payload)
        full_len = 20 + json_len + pyld_len
        
        pkt = bytes('JSONPLUS', 'utf-8') + struct.pack('III', full_len, json_len, pyld_len) + b_json + payload

        print(' '.join('%02x'%b for b in pkt))

        s.sendall(pkt)

        time.sleep(5)        
        