#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <MPU6050.h>
#include "MAX30105.h"
#include "heartRate.h"
#include "algorithm_by_RF.h"  // Ensure correct function header
#include <OneWire.h>
#include <DallasTemperature.h>

#define WIFI_SSID "Infinix"
#define WIFI_PASSWORD "12345678"
#define SERVER_URL "http://192.168.183.18:5000/post-data"

#define ONE_WIRE_BUS 4  // DS18B20 GPIO
WiFiClient espClient;
MPU6050 mpu;
MAX30105 particleSensor;
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);

bool fallDetected = false;
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
int32_t beatsPerMinute;  // Changed from float
int beatAvg;
uint32_t irBuffer[100];
uint32_t redBuffer[100];
float spo2;
int8_t validSpO2;
int8_t validHR;          // Added for heart rate validity
float ratio, corr;       // Added for RF algorithm parameters

void setup_wifi() {
    Serial.println("🔗 Connecting to WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    WiFi.setAutoReconnect(true);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi Connected!");
        Serial.print("📶 IP Address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\n❌ WiFi Connection Failed!");
    }
}

void read_pulse_oximeter() {
    long irValue = particleSensor.getIR();
    if (irValue < 50000) {
        Serial.println("No finger detected!");
        return;
    }

    for (int i = 0; i < 100; i++) {
        irBuffer[i] = particleSensor.getIR();
        redBuffer[i] = particleSensor.getRed();
        delay(10);
    }

    // Corrected function call with proper parameters
    rf_heart_rate_and_oxygen_saturation(
        irBuffer, 100, redBuffer,
        &spo2, &validSpO2,
        &beatsPerMinute, &validHR,
        &ratio, &corr
    );

    // Update heart rate average if valid
    if (validHR) {
        rates[rateSpot++] = (byte)beatsPerMinute;
        rateSpot %= RATE_SIZE;
        beatAvg = 0;
        for (byte x = 0; x < RATE_SIZE; x++) {
            beatAvg += rates[x];
        }
        beatAvg /= RATE_SIZE;
    } else {
        Serial.println("Invalid heart rate reading!");
    }
}

float read_temperature() {
    tempSensor.requestTemperatures();
    return tempSensor.getTempCByIndex(0);
}

void detect_fall() {
    int16_t ax, ay, az;
    mpu.getAcceleration(&ax, &ay, &az);
    float accelX = ax / 16384.0;
    float accelY = ay / 16384.0;
    float accelZ = az / 16384.0;

    if (abs(accelX) > 2.0 || abs(accelY) > 2.0 || abs(accelZ) < 0.3) {
        fallDetected = true;
        Serial.println("⚠ Fall Detected!");
    } else {
        fallDetected = false;
    }
}

void send_data() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("❌ WiFi Disconnected! Attempting to reconnect...");
        setup_wifi();
        return;
    }

    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    read_pulse_oximeter();
    float temperature = read_temperature();
    detect_fall();

    int16_t ax, ay, az;
    mpu.getAcceleration(&ax, &ay, &az);
    float accelX = ax / 16384.0;
    float accelY = ay / 16384.0;
    float accelZ = az / 16384.0;

    String payload = "{";
    payload += "\"heart_rate\": " + String(beatAvg) + ", ";
    payload += "\"spo2\": " + String(spo2, 2) + ", ";
    payload += "\"temperature\": " + String(temperature, 2) + ", ";
    payload += "\"acceleration\": [" + String(accelX, 2) + ", " + String(accelY, 2) + ", " + String(accelZ, 2) + "], ";
    payload += "\"fall_detected\": " + String(fallDetected ? "true" : "false");
    payload += "}";

    Serial.println("📡 Sending Data: " + payload);
    int httpResponseCode = http.POST(payload);
    Serial.print("🌍 HTTP Response: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {
        Serial.println("✅ Data sent successfully!");
    } else {
        Serial.println("❌ HTTP Request Failed!");
    }
    http.end();
}

void setup() {
    Serial.begin(115200);
    setup_wifi();
    Wire.begin(21, 22);

    if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
        Serial.println("❌ MAX30102 not found!");
    } else {
        Serial.println("✅ MAX30102 Initialized!");
    }

    tempSensor.begin();
    Serial.println("✅ DS18B20 Initialized!");

    mpu.initialize();
    if (!mpu.testConnection()) {
        Serial.println("❌ MPU6050 not found!");
    } else {
        Serial.println("✅ MPU6050 Initialized!");
        mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);
    }
}

void loop() {
    send_data();
    delay(1000);
}