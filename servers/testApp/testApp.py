import Tkinter as tk

import array
import socket
import struct
import sys

multicast_group = ('224.3.29.71', 4210)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.2)
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.red_slider   = tk.Scale(self.root, from_=0, to=255, orient='horizontal', command=self.update_values)
        self.green_slider = tk.Scale(self.root, from_=0, to=255, orient='horizontal', command=self.update_values)
        self.blue_slider  = tk.Scale(self.root, from_=0, to=255, orient='horizontal', command=self.update_values)
        self.white_slider = tk.Scale(self.root, from_=0, to=255, orient='horizontal', command=self.update_values)

        self.red_slider.pack()
        self.green_slider.pack()
        self.blue_slider.pack()
        self.white_slider.pack()

        self.root.mainloop()

    def update_values(self, event):
        values = [
            self.red_slider.get(),
            self.green_slider.get(),
            self.blue_slider.get(),
            self.white_slider.get(),
        ]

        sent = sock.sendto(array.array('B', values).tostring(), multicast_group)

app=App()
