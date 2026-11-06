#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

const char* ssid = "YOUR_SSID";      // Wi-Fi 이름
const char* password = "YOUR_PASSWORD";  // Wi-Fi 비밀번호

WebServer server(80);

Servo servo1;
Servo servo2;

int servoPin1 = 21;
int servoPin2 = 22;

int servo1_pos = 0;
int servo2_pos = 0;
bool servos_initialized = false;

void setup() {
  Serial.begin(115200);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.print("WiFi: ");
  Serial.println(WiFi.SSID());
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  
  servo1.attach(servoPin1, 500, 2400);
  servo2.attach(servoPin2, 500, 2400);
  servo1.write(0);
  servo2.write(0);
  servo1_pos = 0;
  servo2_pos = 0;
  servos_initialized = true;
  
  Serial.println("Servos initialized");
  
  server.on("/", handleRoot);
  server.on("/servo", HTTP_POST, handleServo);
  server.on("/status", handleStatus);
  server.on("/reset", handleReset);
  
  server.begin();
  Serial.println("Server started");
}

void loop() {
  server.handleClient();
}

void handleRoot() {
  String html = "<h1>ESP32 Servo Controller</h1>";
  html += "<p>IP: " + WiFi.localIP().toString() + "</p>";
  html += "<p>Servo1 (Pin 21): " + String(servo1_pos) + " degrees</p>";
  html += "<p>Servo2 (Pin 22): " + String(servo2_pos) + " degrees</p>";
  server.send(200, "text/html", html);
}

void handleServo() {
  if (server.hasArg("plain")) {
    DynamicJsonDocument doc(1024);
    deserializeJson(doc, server.arg("plain"));
    
    if (doc.containsKey("servo") && doc.containsKey("angle")) {
      int servo_num = doc["servo"];
      int angle = doc["angle"];
      
      if (angle < -45 || angle > 180) {
        server.send(400, "application/json", "{\"error\":\"Angle range: -45 to 180 degrees\"}");
        return;
      }
      
      bool success = false;
      
      if (servo_num == 1) {
        servo1.write(angle);
        servo1_pos = angle;
        success = true;
        Serial.println("Servo1 position: " + String(angle));
      } else if (servo_num == 2) {
        servo2.write(angle);
        servo2_pos = angle;
        success = true;
        Serial.println("Servo2 position: " + String(angle));
      }
      
      if (success) {
        String response = "{\"servo\":" + String(servo_num) + ",\"angle\":" + String(angle) + "}";
        server.send(200, "application/json", response);
      } else {
        server.send(400, "application/json", "{\"error\":\"Invalid servo number (1 or 2)\"}");
      }
    } else {
      server.send(400, "application/json", "{\"error\":\"servo and angle parameters required\"}");
    }
  } else {
    server.send(400, "application/json", "{\"error\":\"JSON data required\"}");
  }
}

void handleStatus() {
  String json = "{";
  json += "\"wifi\":\"" + WiFi.SSID() + "\",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"servo1_pos\":" + String(servo1_pos) + ",";
  json += "\"servo2_pos\":" + String(servo2_pos) + ",";
  json += "\"initialized\":" + String(servos_initialized ? "true" : "false");
  json += "}";
  server.send(200, "application/json", json);
}

void handleReset() {
  servo1.write(0);
  servo2.write(0);
  servo1_pos = 0;
  servo2_pos = 0;
  
  server.send(200, "application/json", "{\"status\":\"reset_complete\"}");
  Serial.println("Servos reset completed");
}
