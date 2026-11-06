#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "YOUR_SSID";      // Wi-Fi 이름
const char* password = "YOUR_PASSWORD";  // Wi-Fi 비밀번호
WebServer server(80);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  
  server.on("/test", []() {
    Serial.println("Raspberry Pi connected!");
    server.send(200, "text/plain", "ESP32 OK");
  });
  
  server.begin();
}

void loop() {
  server.handleClient();
}