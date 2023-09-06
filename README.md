# BlinkNet
BlinkNet is a system designed for controlling RGBW LEDs across multiple devices from a single control unit via UDP Multicast.

_This rough footage explains what the project does. Unfortunately, the best example I have is set to the "Cha-Cha Slide." No project is perfect._
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/tLIPRsWJwsU/0.jpg)](https://www.youtube.com/watch?v=tLIPRsWJwsU)

## Protocol
Clients and the source form a multicast group, currently with address `224.3.29.71` and port `4210`. There is currently no standard channel of client to server communication. Servers send out packets with the structure:

|                0 |      1 |         2 |        3 |     4...7 | 4(n+1)...4(n+1)+4 |
|------------------|--------|-----------|----------|-----------|-------------------|
| number of lights | opcode | client ID | reserved | RGBW data |      RGBW Data... |

The first byte is the number of lights in the packet, meaning the total packet size is 4n+4 bytes total. The second byte is the opcode, detailed below. The third byte is the device ID (if applicable per the opcode). The fourth byte is reserved, and the remaining data is RGWB data for each LED.

### Opcodes
- **0x00**: Broadcast colors. This is the "normal" mode of operation, and is used when the control unit is broadcasting color data to all devices on the network. It does not set a device ID.
- **0x01**: Individual device colors. This addresses a specific device (via the device ID byte), and only that device should follow the order. Once consumed, the device should ignore broadcast colors until this state is cleared. This should be used sparingly, as the nature of the network means that all device will receive this packet.
- **0x02**: Clear device color. This packet clears the individual color state to allow the device to listen to broadcasts again.
- **0x03**: Global clear hold. Same as **0x02**, but all currently-holding devices should listen.

## Clients
There is currently one client implementation. It is for the Arduino-bootloaded ESP8266-01 WiFi transceiver module, and it drives an ws2812 RGBW LED chain.

## Servers
There are currently two BlinkNet servers. One is a basic test application with RGBW sliders for testing devices. The other is meant for converting audio input to color output on the Raspberry Pi.
