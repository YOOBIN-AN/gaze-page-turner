#include <WiFi.h>

const char* ssid = "YOUR_SSID";      // Wi-Fi 이름
const char* password = "YOUR_PASSWORD";  // Wi-Fi 비밀번호

WiFiServer server(8080);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected! IP: ");
  Serial.println(WiFi.localIP());

  server.begin();  // 포트 8080 열기
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected");
    String line = client.readStringUntil('\n');
    line.trim();
    Serial.print("Command: ");
    Serial.println(line);

    if (line == "PAGE_TURN_LEFT") {
      // 서보 왼쪽 동작 넣기
      client.println("OK");
    } else if (line == "PAGE_TURN_RIGHT") {
      // 서보 오른쪽 동작 넣기
      client.println("OK");
    } else {
      client.println("ERR");
    }
    client.stop();
  }
}