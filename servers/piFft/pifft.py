#!/usr/bin/env python

# Pi FFT Processor/Transmitter
# Used the script from this post as a starting point:
# https://www.raspberrypi.org/forums/viewtopic.php?t=35838&p=454041

import alsaaudio as aa
import smbus
from time import sleep
from struct import unpack
import numpy as np
import audioop
import termplot

import array
import socket
import struct
import sys

multicast_group = ('224.3.29.71', 4210)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.setsockopt(socket.SOL_SOCKET, 25, 'wlan0')
sock.settimeout(0.2)
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

bus=smbus.SMBus(1)

# Set up audio
sample_rate = 14400
#sample_rate = 44100
no_channels = 1
#chunk = 512 # Use a multiple of 8
chunk = 256 # Use a multiple of 8
data_in = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, 'hw:CARD=USB,DEV=0')
data_in.setchannels(no_channels)
data_in.setrate(sample_rate)
data_in.setformat(aa.PCM_FORMAT_S16_LE)
data_in.setperiodsize(chunk)

def calculate_levels(data, bin_width, sample_rate):
    # Convert raw data to numpy array
    data = unpack("%dh"%(len(data)/2),data)
    data = np.array(data, dtype='h')
    # Apply FFT - real data so rfft used
    fourier = np.fft.rfft(data)

    # Remove last element in array to make it the same size as chunk
    fourier = np.delete(fourier, len(fourier)-1)
    #fourier = np.delete(fourier, 10)

    # Find amplitude
    power = np.log10(np.abs(fourier))

    # Arange array into 8 rows for the 8 bars on LED matrix
    power = np.reshape(power,(bin_width, len(power)/bin_width))

    # Collapse the 2-D array to 1-D by averaging columns
    matrix = np.average(power,axis=1)

    # Map the resulting power to an easier-to-use scale
    #print "min: %s max: %s" % (np.min(matrix), np.max(matrix))
    #threshold = 2.8
    threshold = 2.5
    matrix[matrix < threshold] = 0
    max = np.max(matrix)
    max = threshold if max < threshold else max
    matrix = np.interp(matrix, (threshold, max), (0.01, 255.0))

    # Cast values down to int
    matrix = np.int_(matrix)
    bins = np.fft.rfftfreq(len(data), 1.0/sample_rate)
    return matrix

print "Processing....."

num_lights = 3
def make_packet(matrix):
    packet = [
        num_lights,
        0, # broadcast
        0, # id (not needed)
        0, # reserved
    ]

    val1 = matrix[1] # skip the bass
    val2 = matrix[2]
    val3 = matrix[3]

    for _ in range(0, num_lights):
        packet += [
            val1,
            val2,
            val3,
            0, # white
        ]

    return packet

while True:
    # Read data from device
    l,data = data_in.read()
    data_in.pause(1) # Pause capture whilst RPi processes data
    if l:
        # catch frame error
        try:
            matrix = calculate_levels(data, 4, sample_rate)
            #values = [
            #    matrix[1], #skip the bass
            #    matrix[2],
            #    matrix[3],
            #    0,   #white
            #]

            #packet = array.array('B', make_packet(matrix)).tostring()
            sock.sendto(array.array('B', make_packet(matrix)).tostring(), multicast_group)
            #termplot.plot(matrix)
            #print("\033[6;3H")
            #print(matrix)

        except audioop.error, e:
            if e.message !="not a whole number of frames":
                raise e
    sleep(0.001)
    data_in.pause(0) # Resume capture

