#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 04:55:45 2024

@author: john
"""

import json
import struct

TITLE = bytes('JSONPLUS', 'utf-8')

def encode(metadata, payload):
    b_json = bytes(json.dumps(metadata), 'utf-8')
    
    json_len = len(b_json)
    pyld_len = len(payload)
    full_len = 20 + json_len + pyld_len
    
    pkt = bytes('JSONPLUS', 'utf-8') + struct.pack('III', full_len, json_len, pyld_len) + b_json + payload
    return pkt

def try_decode_from_socket(s):
    data = s.recv(8)
    
    if data == TITLE:
        header = s.recv(12)
        if len(header) == 12:
            total_len, json_len, payload_len = struct.unpack('III', header)
            metadata = dict()
            if json_len > 0:
                json_bytes = s.recv(json_len)
                metadata = json.loads(json_bytes)
            payload = s.recv(payload_len)
            return (metadata, payload)
    else:
        return None