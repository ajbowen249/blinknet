/*
    BlinkNet ESP8266 Client
        Alex Bowen 2018
*/

#include <Adafruit_NeoPixel.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#define NEO_PIN    2
#define NUM_LIGHTS 2
Adafruit_NeoPixel display = Adafruit_NeoPixel(NUM_LIGHTS, NEO_PIN, NEO_GRBW + NEO_KHZ800);

#define WIFI_SSID     "Hanshotfirst (2G)"
#define WIFI_PASSWORD "12Parsecs"

#define UDP_PORT 4210
#define UDP_GROUP_0 224
#define UDP_GROUP_1   3
#define UDP_GROUP_2  29
#define UDP_GROUP_3  71
IPAddress multicastGroup(UDP_GROUP_0, UDP_GROUP_1, UDP_GROUP_2, UDP_GROUP_3);

#define MAX_PACKET_LENGTH 255
char packetBuffer[MAX_PACKET_LENGTH];

WiFiUDP Udp;

void setup() {
    initDisplay();
    connectToWifi();
}

void initDisplay() {
    display.begin();
    for (int i = 0; i < NUM_LIGHTS; i++) {
        display.setPixelColor(i, 0, 0, 0, 0);
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
            display.setPixelColor(i, 0, 0, 0, 0);
            display.show();
        }
    }

    Udp.beginMulticast(WiFi.localIP(), multicastGroup, UDP_PORT);
}

void loop() {
    int incomingSize = Udp.parsePacket();

    if (incomingSize > 0) {
        int actualSize = Udp.read(packetBuffer, MAX_PACKET_LENGTH);

        if (actualSize > 0) {
            packetBuffer[actualSize] = 0;
        }

        for (int i = 0; i < NUM_LIGHTS; i++) {
            display.setPixelColor(i, packetBuffer[0], packetBuffer[1], packetBuffer[2], packetBuffer[3]);
            display.show();
        }
    }
}
