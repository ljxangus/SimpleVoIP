#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Echo server program
import socket
import pyaudio
import zlib
import time

CHUNK = 1400
CHANNELS = 1
RATE = 15400
#WAVE_OUTPUT_FILENAME = "server_output.wav"
WIDTH = 1
total_size = 0

p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)


HOST = '127.0.0.1'                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))
data, addr = s.recvfrom(4096)
start_time = time.time()
total_size = total_size + len(data)
print "\r Data speed = %.3f Kbit/s\r" % (total_size*8.0/(time.time()-start_time)/1024)

while data != '':
    de_com_data = zlib.decompress(data)
    stream.write(de_com_data)
    data, addr = s.recvfrom(4096)
    total_size = total_size + len(data)
    print "\r Data speed = %.3f Kbit/s\r" % (total_size*8.0/(time.time()-start_time)/1024)
    #print "Data size = %d, and original data size = %d" %(len(data),len(de_com_data))

'''
frames.append(data)

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
'''

stream.stop_stream()
stream.close()
p.terminate()
conn.close()