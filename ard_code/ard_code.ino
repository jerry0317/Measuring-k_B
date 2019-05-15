const int pingPin = 7; // Trigger Pin of Ultrasonic Sensor
const int echoPin = 6; // Echo Pin of Ultrasonic Sensor


#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

#include <ArduinoJson.h>

#define BMP_SCK 13
#define BMP_MISO 12
#define BMP_MOSI 11
#define BMP_CS 10

#define DELAY 1000

Adafruit_BMP280 bme;

void setup() {
   Serial.begin(9600); // Starting Serial Terminal

   if (!bme.begin()) {
    Serial.println("Could not find a valid BMP280 sensor, check wiring!");
    while (1);
  }
}

void loop() {
   float duration, temperature, pressure;
   StaticJsonDocument<200> doc;

   temperature = bme.readTemperature();
   pressure = bme.readPressure();

   pinMode(pingPin, OUTPUT);
   digitalWrite(pingPin, LOW);
   delayMicroseconds(2);
   digitalWrite(pingPin, HIGH);
   delayMicroseconds(10);
   digitalWrite(pingPin, LOW);
   pinMode(echoPin, INPUT);
   duration = pulseIn(echoPin, HIGH);

   doc["tt_us"] = duration;
   doc["temp"] = temperature;
   doc["pres"] = pressure; 
   serializeJson(doc, Serial);
   Serial.println();
   delay(DELAY);
}
