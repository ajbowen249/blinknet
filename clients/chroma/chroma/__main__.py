from tkinter import *

import array
import json
import socket
import struct
import sys
from urllib import request, parse

multicast_group = '224.3.29.71'
server_address = ('', 4210)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(server_address)
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

chroma_sdk_base = 'http://localhost:54235/razer/chromasdk'

num_lights_default = 3
device_id_default = 1

def init():
    # Register with the Chroma server
    data = {
        'title': 'BlinkNet Razer Chroma Bridge',
        'description': 'Listens in on BlinkNet and pushes colors to Chroma-enabled devices',
        'author': {
            'name': 'Alex Bowen',
            'contact': 'ajbowen249@gmail.com'
        },
        'device_supported': [
            'mouse',
            'mousepad',
            'chromalink'
        ],
        'category': 'application'
    }

    req = request.Request(chroma_sdk_base, data=str(json.dumps(data)).encode('utf-8'))
    req.add_header("content-type", "application/json")
    resp = request.urlopen(req)

    response_body = json.loads(resp.read())
    return response_body['uri']

def bridge(uri):
    packet, address = sock.recvfrom(256)
    r = packet[7]
    g = packet[8]
    b = packet[9]

    # Chroma data is BGR, not RGB
    color = r
    color += (g << 8)
    color += (b << 16)

    data = {
        'effect': 'CHROMA_STATIC',
        'param': { 'color': color },
    }

    req = request.Request(uri + '/mousepad', method='PUT', data=str(json.dumps(data)).encode('utf-8'))
    request.urlopen(req).read()
    req = request.Request(uri + '/mouse', method='PUT', data=str(json.dumps(data)).encode('utf-8'))
    request.urlopen(req).read()


def main(uri):
    while(True):
        bridge(uri)

main(init())
