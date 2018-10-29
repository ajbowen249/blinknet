from tkinter import *

import array
import socket
import struct
import sys

multicast_group = ('224.3.29.71', 4210)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.2)
ttl = struct.pack('b', 1)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

num_lights_default = 2
hold_id_default = 1

class App:
    def __init__(self):
        self.num_lights = num_lights_default
        self.hold_id = hold_id_default

        self.root = Tk()
        self.root.title("BlinkNet Tester")

        self.red_slider   = self.make_scale()
        self.green_slider = self.make_scale()
        self.blue_slider  = self.make_scale()
        self.white_slider = self.make_scale()

        self.begin_hold_button = Button(self.root, text="Hold Current Color", command=self.begin_hold)
        self.clear_hold_button = Button(self.root, text="Clear Hold", command=self.clear_hold)
        self.global_clear_hold_button = Button(self.root, text="Global Clear Hold", command=self.global_clear_hold)

        Label(self.root, text="Red", background="#FF0000").grid(row=0, column=0)
        self.red_slider.grid(row=0, column=1)

        Label(self.root, text="Green", background="#00FF00").grid(row=1, column=0)
        self.green_slider.grid(row=1, column=1)

        Label(self.root, text="Blue", background="#0000FF").grid(row=2, column=0)
        self.blue_slider.grid(row=2, column=1)

        Label(self.root, text="White", background="#FFFFFF").grid(row=3, column=0)
        self.white_slider.grid(row=3, column=1)

        self.begin_hold_button.grid(row=4, column=1)
        self.clear_hold_button.grid(row=5, column=1)
        self.global_clear_hold_button.grid(row=6, column=1)

        self.root.mainloop()


    def get_color_packet(self, opcode=0, id=0):
        packet = [
            self.num_lights,
            opcode,
            id,
            0, # reserved
        ]

        for _ in range(0, self.num_lights):
            packet += [
                self.red_slider.get(),
                self.green_slider.get(),
                self.blue_slider.get(),
                self.white_slider.get()
            ]

        return packet


    def broadcast_values(self, event):
        self.send_packet(self.get_color_packet())


    def begin_hold(self):
        self.send_packet(self.get_color_packet(1, self.hold_id))


    def clear_hold(self):
        self.send_packet(self.get_color_packet(2, self.hold_id))


    def global_clear_hold(self):
        self.send_packet(self.get_color_packet(3))


    def send_packet(self, packet):
        sock.sendto(
            array.array('B', packet).tostring(),
            multicast_group
        )

    def make_scale(self):
        return Scale(
            self.root,
            from_=0,
            to=255,
            orient='horizontal',
            showvalue=0,
            command=self.broadcast_values
        )


app=App()
