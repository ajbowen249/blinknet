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

MULTICAST_GROUP = ('224.3.29.71', 4210)
BUS_INDEX = 2
SAMPLE_RATE = 14400 #44100
CHANNELS = 1
CHUNK = 256 #512
NUM_LIGHTS = 3

def init():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    bus = smbus.SMBus(BUS_INDEX)

    data_in = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, 'hw:CARD=USB,DEV=0')
    data_in.setchannels(CHANNELS)
    data_in.setrate(SAMPLE_RATE)
    data_in.setformat(aa.PCM_FORMAT_S16_LE)
    data_in.setperiodsize(CHUNK)

    return (sock, bus, data_in)

def calculate_levels(data, bin_width):
    # Convert raw data to numpy array
    data = unpack('%dh'%(len(data)/2),data)
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
    matrix = np.interp(matrix, (np.min(matrix), np.max(matrix)), (0.01, 255.0))
    #matrix = np.interp(matrix, (25, np.max(matrix)), (0.01, 50))

    # Cast values down to int
    matrix = np.int_(matrix)
    bins = np.fft.rfftfreq(len(data), 1.0/SAMPLE_RATE)
    return matrix

def make_packet(matrix):
    packet = [
        NUM_LIGHTS,
        0, # broadcast
        0, # id (not needed)
        0, # reserved
    ]

    for _ in range(0, NUM_LIGHTS):
        packet += [
            matrix[1], # skip the bass
            matrix[2],
            matrix[3],
            0, # white
        ]

    return packet

def main():
    print('initializing...')
    sock, bus, data_in = init()
    print('processing')

    while(True):
        l, data = data_in.read()
        data_in.pause(1)
        if l:
            try:
                matrix = calculate_levels(data, 4)
                sock.sendto(array.array('B', make_packet(matrix)).tostring(), MULTICAST_GROUP)

            except audioop.error, e:
                if e.message != 'not a whole number of frames':
                    raise e
        sleep(0.001)
        data_in.pause(0) # Resume capture


while(True):
    try:
        main()
    except Exception as e:
        print(e.message)
        pass
