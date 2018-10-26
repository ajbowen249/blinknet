/*
    BlinkNet ESP8266 Client
        Alex Bowen 2018
*/

#include <Adafruit_NeoPixel.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#include "config.h"

Adafruit_NeoPixel g_display = Adafruit_NeoPixel(NUM_LIGHTS, NEO_PIN, NEO_GRBW + NEO_KHZ800);

IPAddress g_multicastGroup(UDP_GROUP_0, UDP_GROUP_1, UDP_GROUP_2, UDP_GROUP_3);
byte g_packetBuffer[MAX_PACKET_LENGTH];

WiFiUDP g_udp;
bool g_holding;

enum class Opcode : byte {
    Broadcast = 0x00,
    Hold = 0x01,
    ClearHold = 0x02,
    GlobalClearHold = 0x03,
};

inline void blankLight(int light) {
    g_display.setPixelColor(light, 0, 0, 0, 0);
}

void setup() {
    g_holding = false;

    initDisplay();
    connectToWifi();
}

void initDisplay() {
    g_display.begin();
    for (int i = 0; i < NUM_LIGHTS; i++) {
        blankLight(i);
    }

    g_display.show();
}

void connectToWifi() {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(250);

        for (int i = 0; i < NUM_LIGHTS; i++) {
            g_display.setPixelColor(i, 255, 0, 0, 0);
            g_display.show();
        }

        delay(250);

        for (int i = 0; i < NUM_LIGHTS; i++) {
            blankLight(i);
            g_display.show();
        }
    }

    g_udp.beginMulticast(WiFi.localIP(), g_multicastGroup, UDP_PORT);
}

void loop() {
    processPacket();
}

inline void processPacket() {
    int incomingSize = g_udp.parsePacket();

    if (incomingSize > 0) {
        int actualSize = g_udp.read(g_packetBuffer, MAX_PACKET_LENGTH);

        int numSentLights = g_packetBuffer[0];
        Opcode opcode = (Opcode)g_packetBuffer[1];

        if (opcode != Opcode::Broadcast) {
            byte id = g_packetBuffer[2];
            if (
                opcode == Opcode::GlobalClearHold ||
                (id == DEVICE_ID && opcode == Opcode::ClearHold)
            ) {
                g_holding = false;
                return;
            }

            if (id != DEVICE_ID) {
                return;
            }
        }

        if (g_holding) {
            return;
        }

        int processLights = NUM_LIGHTS < numSentLights ? NUM_LIGHTS: numSentLights;

        for (int i = 0; i < processLights; i++) {
            int baseAddress = (i + 1) * BYTES_PER_LIGHT;
            g_display.setPixelColor(
                i,
                g_packetBuffer[baseAddress],
                g_packetBuffer[baseAddress + 1],
                g_packetBuffer[baseAddress + 2],
                g_packetBuffer[baseAddress + 3]
            );
        }

        for (int i = processLights; i < NUM_LIGHTS; i++) {
            blankLight(i);
        }

        if (opcode == Opcode::Hold) {
            g_holding = true;
        }

        g_display.show();
    }
}
