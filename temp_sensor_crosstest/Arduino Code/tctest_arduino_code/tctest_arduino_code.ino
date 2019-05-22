// Temperature Sensor Cross Test - Arduino Side

#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#include "Adafruit_MCP9808.h"
#include <Adafruit_BMP280.h>

#include <ArduinoJson.h>

#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10

#define BMP_SCK  (13)
#define BMP_MISO (12)
#define BMP_MOSI (11)
#define BMP_CS   (10)

#define DELAY 1000

Adafruit_BME680 bme;
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();
Adafruit_BMP280 bmp(BMP_CS, BMP_MOSI, BMP_MISO,  BMP_SCK);

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!bme.begin()) {
    Serial.println("Could not find a valid BME680 sensor, check wiring!");
    while (1);
  }

  if (!tempsensor.begin(0x18)) {
    Serial.println("Couldn't find MCP9808! Check your connections and verify the address is correct.");
    while (1);
  }

  if (!bmp.begin()) {
    Serial.println(F("Could not find a valid BMP280 sensor, check wiring!"));
    while (1);
  }

  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150);

  tempsensor.setResolution(3);

  /* Default settings from datasheet. */
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
                  Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
                  Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
                  Adafruit_BMP280::FILTER_X16,      /* Filtering. */
                  Adafruit_BMP280::STANDBY_MS_500); /* Standby time. */
}

void loop() {
  float temperature, pressure, humidity, temperature_precise, temperature_bmp, pressure_bmp;
  StaticJsonDocument<200> doc;
  
  if (! bme.performReading()) {
    Serial.println("Failed to perform reading on BME680");
    return;
  }

  temperature = bme.temperature;
  pressure = bme.pressure;
  humidity = bme.humidity;
  temperature_precise = tempsensor.readTempC();
  temperature_bmp = bmp.readTemperature();
  pressure_bmp = bmp.readPressure();

  doc["temp"] = temperature;
  doc["pres"] = pressure;
  doc["hum"] = humidity;
  doc["temp_p"] = temperature_precise;
  doc["temp_b"] = temperature_bmp;
  doc["pres_b"] = pressure_bmp;
  
  serializeJson(doc, Serial);
  Serial.println();
  delay(DELAY);
}
