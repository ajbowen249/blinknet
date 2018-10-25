/*
    BlinkNet ESP8266 Client
        Alex Bowen 2018
*/

#include <Adafruit_NeoPixel.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// IMPROVE: Determine this from some static ESP data, if
//          such a thing exists, and print it out.
#define DEVICE_ID 1

#define NEO_PIN    2
#define NUM_LIGHTS 2
#define BYTES_PER_LIGHT 4
Adafruit_NeoPixel display = Adafruit_NeoPixel(NUM_LIGHTS, NEO_PIN, NEO_GRBW + NEO_KHZ800);

#define WIFI_SSID     "Hanshotfirst (2G)"
#define WIFI_PASSWORD "12Parsecs"

#define UDP_PORT 4210
#define UDP_GROUP_0 224
#define UDP_GROUP_1   3
#define UDP_GROUP_2  29
#define UDP_GROUP_3  71
IPAddress multicastGroup(UDP_GROUP_0, UDP_GROUP_1, UDP_GROUP_2, UDP_GROUP_3);

#define MAX_PACKET_LENGTH 256
char packetBuffer[MAX_PACKET_LENGTH];

WiFiUDP g_udp;
bool g_holding;

inline void blankLight(int light) {
    display.setPixelColor(light, 0, 0, 0, 0);
}

void setup() {
    g_holding = false;

    initDisplay();
    connectToWifi();
}

void initDisplay() {
    display.begin();
    for (int i = 0; i < NUM_LIGHTS; i++) {
        blankLight(i);
    }

    display.show();
}

void connectToWifi() {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(250);

        for (int i = 0; i < NUM_LIGHTS; i++) {
            display.setPixelColor(i, 255, 0, 0, 0);
            display.show();
        }

        delay(250);

        for (int i = 0; i < NUM_LIGHTS; i++) {
            blankLight(i);
            display.show();
        }
    }

    g_udp.beginMulticast(WiFi.localIP(), multicastGroup, UDP_PORT);
}

void loop() {
    processPacket();
}

inline void processPacket() {
    int incomingSize = g_udp.parsePacket();

    if (incomingSize > 0) {
        int actualSize = g_udp.read(packetBuffer, MAX_PACKET_LENGTH);

        int numSentLights = packetBuffer[0];
        int processLights = NUM_LIGHTS < numSentLights ? NUM_LIGHTS: numSentLights;

        for (int i = 0; i < processLights; i++) {
            int baseAddress = (i + 1) * BYTES_PER_LIGHT;
            display.setPixelColor(
                i,
                packetBuffer[baseAddress],
                packetBuffer[baseAddress + 1],
                packetBuffer[baseAddress + 2],
                packetBuffer[baseAddress + 3]
            );
        }

        for (int i = processLights; i < NUM_LIGHTS; i++) {
            blankLight(i);
        }

        display.show();
    }
}
