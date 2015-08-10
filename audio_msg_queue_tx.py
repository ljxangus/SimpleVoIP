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


class audio_rx(gr.hier_block2):
    def __init__(self, audio_input_dev):
        gr.hier_block2.__init__(self, "audio_rx",
				gr.io_signature(0, 0, 0), # Input signature
				gr.io_signature(0, 0, 0)) # Output signature
        self.sample_rate = sample_rate = 8000
        src = audio.source(sample_rate, audio_input_dev)
        src_scale = gr.multiply_const_ff(32767)
        f2s = gr.float_to_short()
        voice_coder = vocoder.gsm_fr_encode_sp()
        self.packets_from_encoder = gr.msg_queue()
        packet_sink = gr.message_sink(33, self.packets_from_encoder, False)
        self.connect(src, src_scale, f2s, voice_coder, packet_sink)

        #if(options.to_file is not None):
        #    self.sink = gr.file_sink(gr.sizeof_gr_complex, options.to_file)
        #else:
        #    self.sink = gr.null_sink(gr.sizeof_gr_complex)

    def get_encoded_voice_packet(self):
        return self.packets_from_encoder.delete_head()
        

class socket_init():
    def __init__(self,addr):
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class my_top_block(gr.top_block):

    def __init__(self,options):
        gr.top_block.__init__(self)
        self.audio_rx = audio_rx(options.audio_input)
        self.send_socket = socket_init(addr=(options.ip_addr,options.port))

        self.connect(self.audio_rx)
        print "tb initial ended"

    def send_pkt(self,payload):
        self.send_socket.sock.sendto(payload,self.send_socket.addr)            

# /////////////////////////////////////////////////////////////////////////////
#                                   main
# /////////////////////////////////////////////////////////////////////////////

def main():

    def send_pkt(payload='', eof=False):
        return tb.send_pkt(payload)

    def rx_callback(ok, payload):
        print "ok = %r, payload = '%s'" % (ok, payload)

    parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")

    parser.add_option("-M", "--megabytes", type="eng_float", default=0,
                      help="set megabytes to transmit [default=inf]")
    parser.add_option("","--ip_addr", type="string",default='127.0.0.1',
                      help="IP address of Destination")
    parser.add_option("","--port", type="int", default=10008,
                      help="Port address of Destination")
    parser.add_option("-I", "--audio-input", type="string", default="",
                      help="pcm input device name.  E.g., hw:0,0 or /dev/dsp")
    parser.add_option("","--to-file", default=None,
                      help="Output file for modulated samples")

    (options, args) = parser.parse_args ()

    if len(args) != 0:
        parser.print_help()
        sys.exit(1)

    # build the graph
    tb = my_top_block(options)

    #r = gr.enable_realtime_scheduling()
    #if r != gr.RT_OK:
        #print "Warning: failed to enable realtime scheduling"


    print "top_block started!"
    tb.start()                       # start flow graph

    # generate and send packets
    nbytes = int(1e6 * options.megabytes)
    n = 0
    pktno = 0

    while nbytes == 0 or n < nbytes:
        packet = tb.audio_rx.get_encoded_voice_packet()
        s = packet.to_string()
        # Change the packet sending method to using UDP
        send_pkt(s)
        n += len(s)
        sys.stderr.write('.')
        pktno += 1
        
    tb.wait()                       # wait for it to finish


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
	pass