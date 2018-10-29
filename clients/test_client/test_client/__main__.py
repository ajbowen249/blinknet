from tkinter import *

import array
import socket
import struct
import sys

multicast_group = '224.3.29.71'
server_address = ('', 4210)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(server_address)
group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# IMPROVE: Stick this in the gui
num_lights_default = 2
device_id_default = 1

class App:
    def __init__(self):
        self.device_id = device_id_default
        self.num_lights = num_lights_default

        self.root = Tk()
        self.root.title("BlinkNet Fake Client")

        self.root.after(10, self.update)

        self.root.mainloop()

    def update(self):
        data, address = sock.recvfrom(256)
        self.handle_packet(data)
        self.root.after(10, self.update)

    def handle_packet(self, packet):
        r = packet[4]
        g = packet[5]
        b = packet[6]
        color = '#%02x%02x%02x' % (r, g, b)
        self.root.configure(background=color)

app=App()
