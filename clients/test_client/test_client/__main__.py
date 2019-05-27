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

device_id_default = 1

class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("BlinkNet Fake Client")

        self.l1 = Label(self.root, width=10, height=5)
        self.l1.grid(row=0, column=0)

        self.l2 = Label(self.root, width=10, height=5)
        self.l2.grid(row=0, column=1)

        self.l3 = Label(self.root, width=10, height=5)
        self.l3.grid(row=0, column=2)

        self.root.after(1, self.update)

        self.root.mainloop()

    def update(self):
        data, address = sock.recvfrom(256)
        self.handle_packet(data)
        self.root.after(1, self.update)

    def handle_packet(self, packet):
        r = packet[4]
        g = packet[5]
        b = packet[6]
        color = '#%02x%02x%02x' % (r, g, b)
        self.l1.configure(background=color)

        r = packet[8]
        g = packet[9]
        b = packet[10]
        color = '#%02x%02x%02x' % (r, g, b)
        self.l2.configure(background=color)

        r = packet[12]
        g = packet[13]
        b = packet[14]
        color = '#%02x%02x%02x' % (r, g, b)
        self.l3.configure(background=color)

app=App()
