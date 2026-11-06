#include <WiFi.h>

const char* ssid = "YOUR_SSID";      // Wi-Fi 이름
const char* password = "YOUR_PASSWORD";  // Wi-Fi 비밀번호

void setup() {
  Serial.begin(115200);
  delay(500);  // 시리얼 초기화 안정화 대기
  Serial.println();
  Serial.println("=== ESP32 WiFi Test ===");

  // 스테이션 모드로 설정
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);

  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  // 연결될 때까지 대기
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // 연결 성공 시
  Serial.println("\n[OK] WiFi connected!");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 2초마다 연결 상태 체크
  static unsigned long t = 0;
  if (millis() - t > 2000) {
    t = millis();
    if (WiFi.status() == WL_CONNECTED) {
      Serial.print("[Connected] IP: ");
      Serial.println(WiFi.localIP());
    } else {
      Serial.println("[Disconnected] WiFi not connected");
    }
  }
}