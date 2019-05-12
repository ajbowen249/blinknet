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
SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK = 1024
NUM_LIGHTS = 3

SATURATION = 1
VALUE = 1

FFT_BINS = 64

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

def get_raw_fft(data, threshold):
    # Convert raw data to numpy array
    data = unpack('%dh' % (len(data) / 2), data)
    data = np.array(data, dtype='h')

    # Apply FFT - real data so rfft used
    fourier = np.fft.rfft(data)
    # print(np.fft.fftfreq(len(data), 1.0/SAMPLE_RATE)[:512])
    # exit(0)

    # Remove last element in array to make it the same size as chunk
    fourier = np.delete(fourier, len(fourier) - 1)

    # Find amplitude
    power = np.log10(np.abs(fourier))

    # Cut off at threshold and normalize 0-1
    power[power < threshold] = 0
    max = np.max(power)
    max = threshold if max < threshold else max
    power = np.interp(power, (threshold, max), (0.01, 1.0))

    return power

def post_process(power, low_scaler, mid_scaler, high_scaler, bass_cutoff, mid_start, treble_start):
    # Musical frequencies jump up exponentially with note value.
    # What we want to do is separate bass, midrange, and treble
    # out into three different groups. The ranges we're allocating
    # are approximately:
    #
    # 1. 43-172Hz
    # 2. 215-1292Hz
    # 3. 1378-21964Hz
    # This is based on the allocated rfft bins for a 1024-point sample
    # at a 44100Hz sample rate. Those choices line up as close as we
    # can get to the base, midrange, and treble frequencies as defined
    # by this chart:
    # http://www.troelsgravesen.dk/frequency_ranges_files/frequency-bands.jpg

    all_bass = power[bass_cutoff:mid_start]
    all_mid = power[mid_start:treble_start]
    all_treble = power[treble_start:]

    bass = min(1.0, np.max(all_bass) * low_scaler)
    mid = min(1.0, np.max(all_mid) * mid_scaler)
    treble = min(1.0, np.max(all_treble) * high_scaler)

    levels = np.array([bass, mid, treble])

    return levels

def make_packet(matrix):
    packet = [
        NUM_LIGHTS,
        0, # broadcast
        0, # id (not needed)
        0, # reserved
    ]

    light_1 = colorsys.hsv_to_rgb(matrix[0], SATURATION, matrix[0])
    light_2 = colorsys.hsv_to_rgb(matrix[1], SATURATION, matrix[1])
    light_3 = colorsys.hsv_to_rgb(matrix[2], SATURATION, matrix[2])

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
    bus_index = 1 #2
    device = 'plughw:CARD=Microphone,DEV=0'
    threshold = 2.5

    low_scaler = 1
    mid_scaler = 1
    high_scaler = 1

    bass_cutoff = 3
    mid_start = 10
    treble_start = 30

    parser = argparse.ArgumentParser(description='FFT transmistter')
    parser.add_argument("--print-defaults", dest="print_defaults", action="store_true", help="print out default values")
    parser.add_argument('--bus-index', action='store', dest='bus_index', type=int)
    parser.add_argument('--device', action='store', dest='device')

    parser.add_argument('--threshold', action='store', dest='threshold', type=float)

    parser.add_argument('--low-scaler', action='store', dest='low_scaler', type=float)
    parser.add_argument('--mid-scaler', action='store', dest='mid_scaler', type=float)
    parser.add_argument('--high-scaler', action='store', dest='high_scaler', type=float)

    parser.add_argument('--bass-cutoff', action='store', dest='bass_cutoff', type=int)
    parser.add_argument('--mid-start', action='store', dest='mid_start', type=int)
    parser.add_argument('--treble-start', action='store', dest='treble_start', type=int)

    ns = parser.parse_args(sys.argv[1:])
    if ns.print_defaults:
        print(json.dumps({
            'bus_index': bus_index,
            'device': device,

            'threshold': threshold,

            'low_scaler': low_scaler,
            'mid_scaler': mid_scaler,
            'high_scaler': high_scaler,

            'bass_cutoff': bass_cutoff,
            'mid_start': mid_start,
            'treble_start': treble_start,
        }))

        sys.exit()


    if ns.bus_index:
        bus_index = ns.bus_index

    if ns.device:
        device = ns.device

    if ns.threshold:
        threshold = ns.threshold

    if ns.low_scaler:
        low_scaler = ns.low_scaler

    if ns.mid_scaler:
        mid_scaler = ns.mid_scaler

    if ns.high_scaler:
        high_scaler = ns.high_scaler

    if ns.bass_cutoff:
        bass_cutoff = ns.bass_cutoff

    if ns.mid_start:
        mid_start = ns.mid_start

    if ns.treble_start:
        treble_start = ns.treble_start

    return (bus_index, device, threshold, low_scaler, mid_scaler, high_scaler, bass_cutoff, mid_start, treble_start)


def main():
    (bus_index, device, threshold, low_scaler, mid_scaler, high_scaler, bass_cutoff, mid_start, treble_start) = get_params()

    print('initializing...')
    sock, bus, data_in = init(bus_index, device)

    print('processing')

    while(True):
        l, data = data_in.read()
        data_in.pause(1)
        if l:
            try:
                power = get_raw_fft(data, threshold)
                matrix = post_process(power, low_scaler, mid_scaler, high_scaler, bass_cutoff, mid_start, treble_start)
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
