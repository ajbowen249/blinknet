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

# Improve: These could be added to the UI, but it's not currently worth it.
num_lights = 2

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BlinkNet Tester")

        self.red_slider   = tk.Scale(self.root, from_=0, to=255, orient='horizontal', command=self.broadcast_values)
        self.green_slider = tk.Scale(self.root, from_=0, to=255, orient='horizontal', command=self.broadcast_values)
        self.blue_slider  = tk.Scale(self.root, from_=0, to=255, orient='horizontal', command=self.broadcast_values)
        self.white_slider = tk.Scale(self.root, from_=0, to=255, orient='horizontal', command=self.broadcast_values)

        w = tk.Label(self.root, text="Global Red")
        w.pack()
        self.red_slider.pack()

        w = tk.Label(self.root, text="Global Green")
        w.pack()
        self.green_slider.pack()

        w = tk.Label(self.root, text="Global Blue")
        w.pack()
        self.blue_slider.pack()

        w = tk.Label(self.root, text="Global White")
        w.pack()
        self.white_slider.pack()

        self.root.mainloop()

    def broadcast_values(self, event):
        packet = [
            num_lights,
            0, # broadcast
            0, # not needed
            0, # reserved
        ]

        for _ in range(0, num_lights):
            packet += [
                self.red_slider.get(),
                self.green_slider.get(),
                self.blue_slider.get(),
                self.white_slider.get()
            ]

        sock.sendto(array.array('B', packet).tostring(), multicast_group)

app=App()
