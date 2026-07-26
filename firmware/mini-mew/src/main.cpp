// pocket-mew firmware (example)
// ESP32 + FSR + button → HTTPS POST touch events to your relay.
// Configure Wi-Fi / host via include/secrets.h (see secrets.h.example).

#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include "secrets.h"

#define FSR_PIN            A0
#define BTN_PIN            D1
#define FSR_THRESHOLD      200
#define SAMPLE_INTERVAL_MS 50
#define MAX_SAMPLES        120

bool fsrActive = false;
int fsrPeakRaw = 0;
unsigned long fsrStartTime = 0;
unsigned long lastSampleTime = 0;

int curveBuf[MAX_SAMPLES];
int curveLen = 0;

bool btnActive = false;
unsigned long btnStartTime = 0;
bool lastBtnState = HIGH;

void setup() {
  Serial.begin(115200);
  pinMode(BTN_PIN, INPUT_PULLUP);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nconnected");
}

void sendEvent(const char* type, int peakRaw, unsigned long durationMs,
               int* curve, int len) {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    delay(2000);
  }

  WiFiClientSecure client;
  client.setInsecure();  // demo only — pin certs in production if you can
  client.setHandshakeTimeout(30);

  HTTPClient http;
  http.setReuse(false);
  http.begin(client, TOUCH_HOST, TOUCH_PORT, TOUCH_PATH, true);
  http.addHeader("Content-Type", "application/json");
  // Optional: http.addHeader("Authorization", "Bearer " YOUR_TOKEN);

  String curveStr = "[";
  if (curve != nullptr && len > 0) {
    for (int i = 0; i < len; i++) {
      curveStr += String(curve[i]);
      if (i < len - 1) curveStr += ",";
    }
  }
  curveStr += "]";

  String body = String("{\"type\":\"") + type +
                "\",\"peak_raw\":" + String(peakRaw) +
                ",\"duration_ms\":" + String(durationMs) +
                ",\"curve\":" + curveStr + "}";

  int code = http.POST(body);
  Serial.printf("POST %s peak=%d dur=%lums n=%d -> %d\n",
                type, peakRaw, durationMs, len, code);
  http.end();
  delay(100);
}

void loop() {
  unsigned long now = millis();

  bool btnState = digitalRead(BTN_PIN);
  if (btnState == LOW && lastBtnState == HIGH) {
    btnActive = true;
    btnStartTime = now;
  } else if (btnState == HIGH && lastBtnState == LOW) {
    if (btnActive) {
      sendEvent("button", 0, now - btnStartTime, nullptr, 0);
      btnActive = false;
    }
  }
  lastBtnState = btnState;

  int fsrVal = analogRead(FSR_PIN);
  if (fsrVal > FSR_THRESHOLD) {
    if (!fsrActive) {
      fsrActive = true;
      fsrStartTime = now;
      fsrPeakRaw = fsrVal;
      curveLen = 0;
      lastSampleTime = now;
      curveBuf[curveLen++] = fsrVal;
    } else {
      if (fsrVal > fsrPeakRaw) fsrPeakRaw = fsrVal;
      if (now - lastSampleTime >= SAMPLE_INTERVAL_MS && curveLen < MAX_SAMPLES) {
        curveBuf[curveLen++] = fsrVal;
        lastSampleTime = now;
      }
    }
  } else if (fsrActive) {
    sendEvent("touch", fsrPeakRaw, now - fsrStartTime, curveBuf, curveLen);
    fsrActive = false;
    fsrPeakRaw = 0;
    curveLen = 0;
  }

  delay(20);
}
