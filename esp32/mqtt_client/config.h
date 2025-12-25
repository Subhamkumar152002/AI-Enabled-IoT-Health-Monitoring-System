#ifndef CONFIG_H
#define CONFIG_H

// WiFi Credentials
#define WIFI_SSID "Infinix"
#define WIFI_PASSWORD "12345678"

// MQTT Broker Settings
#define MQTT_BROKER "192.168.183.18"  // e.g., "192.168.1.100"
#define MQTT_PORT 1883
#define MQTT_USERNAME "YOUR_MQTT_USERNAME"  // Optional
#define MQTT_PASSWORD "YOUR_MQTT_PASSWORD"  // Optional

// MQTT Topics
#define TOPIC_HEART_RATE "sensors/heart_rate"
#define TOPIC_SPO2 "sensors/spo2"
#define TOPIC_TEMPERATURE "sensors/temperature"
#define TOPIC_ACCELERATION "sensors/acceleration"
#define TOPIC_FALL_ALERT "alerts/fall"

#endif  // CONFIG_H
