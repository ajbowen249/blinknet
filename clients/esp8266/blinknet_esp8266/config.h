#ifndef __CONFIG_H__
#define __CONFIG_H__

// IMPROVE: Determine this from some static ESP data, if
//          such a thing exists, and print it out.
#define DEVICE_ID 1

#define NEO_PIN    2
#define NUM_LIGHTS 2
#define BYTES_PER_LIGHT 4

#define WIFI_SSID     "Hanshotfirst (2G)"
#define WIFI_PASSWORD "12Parsecs"

#define UDP_PORT 4210
#define UDP_GROUP_0 224
#define UDP_GROUP_1   3
#define UDP_GROUP_2  29
#define UDP_GROUP_3  71

#define MAX_PACKET_LENGTH 256

#endif // __CONFIG_H__
