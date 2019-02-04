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
import colorsys

MULTICAST_GROUP = ('224.3.29.71', 4210)
BUS_INDEX = 2
SAMPLE_RATE = 14400 #44100
CHANNELS = 1
CHUNK = 256 #512
NUM_LIGHTS = 3

SATURATION = 1
VALUE = 1

def init():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    bus = smbus.SMBus(BUS_INDEX)

    data_in = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, 'plughw:CARD=Microphone,DEV=0')
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
    matrix = np.average(power, axis=1)

    # Map the resulting power to an easier-to-use scale
    threshold = 2.5
    matrix[matrix < threshold] = 0
    max = np.max(matrix)
    max = threshold if max < threshold else max
    matrix = np.interp(matrix, (threshold, max), (0.01, 1.0))
    # matrix = np.interp(matrix, (np.min(matrix), np.max(matrix)), (0.01, 1.0))

    bins = np.fft.rfftfreq(len(data), 1.0/SAMPLE_RATE)
    #print(bins)
    return matrix

def make_packet(matrix):
    # matrix comes in with 32 values. Drop the lowest and highest to get 30
    matrix = np.delete(matrix, 0)
    matrix = np.delete(matrix, len(matrix)-1)

    # 15 is a multiple of 3. Compress into 3 values
    matrix = np.reshape(matrix,(3, 10))
    matrix = np.average(matrix, axis=1)


    packet = [
        NUM_LIGHTS,
        0, # broadcast
        0, # id (not needed)
        0, # reserved
    ]

    light_1 = colorsys.hsv_to_rgb(matrix[0], SATURATION, min(1.0, matrix[0] * 2))
    light_2 = colorsys.hsv_to_rgb(matrix[1], SATURATION, min(1.0, matrix[1] * 2))
    light_3 = colorsys.hsv_to_rgb(matrix[2], SATURATION, min(1.0, matrix[2] * 2))

    packet += [
        int(light_1[0] * 255),
        int(light_1[1] * 255),
        int(light_1[2] * 255),
        0
    ]

    packet += [
        int(light_2[0] * 255),
        int(light_2[1] * 255),
        int(light_2[2] * 255),
        0
    ]

    packet += [
        int(light_3[0] * 255),
        int(light_3[1] * 255),
        int(light_3[2] * 255),
        0
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
                matrix = calculate_levels(data, 32)
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
        if e and e.message:
            print(e.message)
            exit(0)
