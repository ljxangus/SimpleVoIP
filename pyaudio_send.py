#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import pyaudio
import zlib, time

#record
CHUNK = 1400
WIDTH = 1
CHANNELS = 1
RATE = 15400
RECORD_SECONDS = 100

HOST = '127.0.0.1'    # The remote host
PORT = 50007              # The same port as used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#s.connect((HOST, PORT))

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

print("*recording")

start_time = time.time()
total_size = 0

for i in range(0, int(RATE/CHUNK*RECORD_SECONDS)):
    data  = stream.read(CHUNK)
    com_data = zlib.compress(data)
    s.sendto(com_data,(HOST,PORT))
    stream.write(data, CHUNK)
    total_size = total_size + len(com_data)
    print "i=%d"%i
    print "Type of data=%s, and size=%d" % (type(com_data),len(com_data))
    print "\r Data speed = %.3f Kbit/s\r" % (total_size*8.0/(time.time()-start_time)/1024)

print("*done recording")

stream.stop_stream()
stream.close()
p.terminate()
s.close()

print("*closed")