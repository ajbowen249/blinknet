#!/usr/bin/env python

# Pi FFT Processor/Transmitter
# Used the script from this post as a starting point:
# https://www.raspberrypi.org/forums/viewtopic.php?t=35838&p=454041

import alsaaudio as aa
import argparse
import array
import audioop
import colorsys
import json
import numpy as np
import smbus
import socket
import struct
import sys
import termplot

from struct import unpack
from time import sleep

MULTICAST_GROUP = ('224.3.29.71', 4210)
SAMPLE_RATE = 14400 #44100
CHANNELS = 1
CHUNK = 256 #512
NUM_LIGHTS = 3

SATURATION = 1
VALUE = 1

def init(bus_index, device):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    bus = smbus.SMBus(bus_index)

    data_in = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, device)
    data_in.setchannels(CHANNELS)
    data_in.setrate(SAMPLE_RATE)
    data_in.setformat(aa.PCM_FORMAT_S16_LE)
    data_in.setperiodsize(CHUNK)

    return (sock, bus, data_in)

def get_raw_fft(data, fft_bins):
    # Convert raw data to numpy array
    data = unpack('%dh' % (len(data) / 2), data)
    data = np.array(data, dtype='h')

    # Apply FFT - real data so rfft used
    fourier = np.fft.rfft(data)

    # Remove last element in array to make it the same size as chunk
    fourier = np.delete(fourier, len(fourier) - 1)

    # Find amplitude
    power = np.log10(np.abs(fourier))

    # Reshape the array to the number of bins we want
    power = np.reshape(power,(fft_bins, len(power) / fft_bins))

    # Collapse the 2-D array to 1-D by averaging columns
    matrix = np.average(power, axis=1)

    # Map the resulting power to an easier-to-use scale
    threshold = 2.5
    matrix[matrix < threshold] = 0
    max = np.max(matrix)
    max = threshold if max < threshold else max
    matrix = np.interp(matrix, (threshold, max), (0.01, 1.0))

    return matrix

def merge_bins(matrix, fft_bins):
    if fft_bins == 8:
        # 8->6->3
        matrix = np.delete(matrix, 0)
        matrix = np.delete(matrix, len(matrix) - 1)

        matrix = np.reshape(matrix,(3, 2))
        matrix = np.average(matrix, axis=1)
    elif fft_bins == 16:
        # 16->15->3
        matrix = np.delete(matrix, 0)

        matrix = np.reshape(matrix,(3, 5))
        matrix = np.average(matrix, axis=1)
    elif fft_bins == 32:
        # 32->30->3
        matrix = np.delete(matrix, 0)
        matrix = np.delete(matrix, len(matrix) - 1)

        matrix = np.reshape(matrix,(3, 10))
        matrix = np.average(matrix, axis=1)
    elif fft_bins == 64:
        # 64->63->3
        matrix = np.delete(matrix, 0)

        matrix = np.reshape(matrix,(3, 21))
        matrix = np.average(matrix, axis=1)

    return matrix

def make_packet(matrix):
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

def get_params():
    bus_index = 2
    device = 'plughw:CARD=Microphone,DEV=0'
    fft_bins = 32

    parser = argparse.ArgumentParser(description='FFT transmistter')
    parser.add_argument("--print-defaults", dest="print_defaults", action="store_true", help="print out default values")
    parser.add_argument('--bus-index', action='store', dest='bus_index', type=int)
    parser.add_argument('--device', action='store', dest='device')
    parser.add_argument('--fft-bins', action='store', dest='fft_bins', type=int)

    ns = parser.parse_args(sys.argv[1:])
    if ns.print_defaults:
        print(json.dumps({
            'bus_index': bus_index,
            'device': device,
            'fft_bins': fft_bins,
        }))

        sys.exit()


    if ns.bus_index:
        bus_index = ns.bus_index

    if ns.device:
        device = ns.device

    if ns.fft_bins:
        fft_bins = ns.fft_bins

    return (bus_index, device, fft_bins)


def main():
    (bus_index, device, fft_bins) = get_params()

    print('initializing...')
    sock, bus, data_in = init(bus_index, device)

    print('processing')

    while(True):
        l, data = data_in.read()
        data_in.pause(1)
        if l:
            try:
                matrix = get_raw_fft(data, fft_bins)
                sock.sendto(array.array('B', make_packet(merge_bins(matrix, fft_bins))).tostring(), MULTICAST_GROUP)

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
