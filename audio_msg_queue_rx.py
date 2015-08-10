#!/usr/bin/python
#!/usr/bin/env python
#
# Copyright 2005-2007,2009,2011 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr, audio
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser

from gnuradio import digital
from gnuradio import vocoder

import random
import time
import struct
import sys
import socket

#import os
#print os.getpid()
#raw_input('Attach and press enter')


class audio_tx(gr.hier_block2):
    def __init__(self, audio_output_dev):
        gr.hier_block2.__init__(self, "audio_tx",
                gr.io_signature(0, 0, 0), # Input signature
                gr.io_signature(0, 0, 0)) # Output signature
                
        self.sample_rate = sample_rate = 8000
        self.packet_src = gr.message_source(33)
        voice_decoder = vocoder.gsm_fr_decode_ps()
        s2f = gr.short_to_float ()
        sink_scale = gr.multiply_const_ff(1.0/32767.)
        audio_sink = audio.sink(sample_rate, audio_output_dev)
        self.connect(self.packet_src, voice_decoder, s2f, sink_scale, audio_sink)
        
    def msgq(self):
        return self.packet_src.msgq()
        

class socket_init():
    def __init__(self,ip_addr,port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip_addr, port))

class my_top_block(gr.top_block):

    def __init__(self,options):
        gr.top_block.__init__(self)
        self.audio_tx = audio_tx(options.audio_output)
        self.recv_socket = socket_init(ip_addr=options.ip_addr,port=options.port)

        self.connect(self.audio_tx)
        print "tb initial ended"

    def recv_pkt(self):
        payload,addr = self.recv_socket.sock.recvfrom(4096) 
        return payload           

# /////////////////////////////////////////////////////////////////////////////
#                                   main
# /////////////////////////////////////////////////////////////////////////////
global n_rcvd, n_right

def main():
    global n_rcvd, n_right

    n_rcvd = 0
    n_right = 0

    def rx_callback():
        while 1:
            print "Start to receive the packet"
            payload = tb.recv_pkt()
            if payload != 0:
                ok = True
            else:
                ok = False
            global n_rcvd, n_right
            n_rcvd += 1
            if ok:
                n_right += 1

            #print "Type of the payload is %s" % type(payload)
            tb.audio_tx.msgq().insert_tail(gr.message_from_string(payload))
            print "ok = %r  n_rcvd = %4d  n_right = %4d" % (ok, n_rcvd, n_right)

    parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")

    parser.add_option("-M", "--megabytes", type="eng_float", default=0,
                      help="set megabytes to transmit [default=inf]")
    parser.add_option("","--ip_addr", type="string",default='127.0.0.1',
                      help="IP address of Source")
    parser.add_option("","--port", type="int", default=10008,
                      help="Port address of Source")
    parser.add_option("-O", "--audio-output", type="string", default="",
                      help="pcm output device name.  E.g., hw:0,0 or /dev/dsp")
    parser.add_option("","--from-file", default=None,
                      help="input file of samples to demod")

    (options, args) = parser.parse_args ()

    if len(args) != 0:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # build the graph
    tb = my_top_block(options)

    #r = gr.enable_realtime_scheduling()
    #if r != gr.RT_OK:
        #print "Warning: failed to enable realtime scheduling"


    #th = threading.Thread(target=rx_callback)
    #th.start()
    #print "callback thread and top_block started!"
    tb.start()                       # start flow graph
    print "top_block started!"

    rx_callback()

    tb.wait()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass