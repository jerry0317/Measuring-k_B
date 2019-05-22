#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#include "Adafruit_MCP9808.h"

#include <ArduinoJson.h>

const int pingPin = 7; // Trigger Pin of Ultrasonic Sensor
const int echoPin = 6; // Echo Pin of Ultrasonic Sensor

#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10

#define DELAY 1000

Adafruit_BME680 bme;
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();

void setup() {
  Serial.begin(9600); // Starting Serial Terminal
  while (!Serial);

  if (!bme.begin()) {
    Serial.println("Could not find a valid BME680 sensor, check wiring!");
    while (1);
  }

  if (!tempsensor.begin(0x18)) {
    Serial.println("Couldn't find MCP9808! Check your connections and verify the address is correct.");
    while (1);
  }

  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150);

  tempsensor.setResolution(3);
}

void loop() {
   float duration, temperature, pressure;
   StaticJsonDocument<200> doc;

   if (! bme.performReading()) {
    Serial.println("Failed to perform reading on BME680");
    return;
   }

   temperature = tempsensor.readTempC();
   pressure = bme.pressure;

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
