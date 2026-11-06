#include <WiFi.h>

const char* ssid = "YOUR_SSID";      // Wi-Fi 이름
const char* password = "YOUR_PASSWORD";  // Wi-Fi 비밀번호

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("ESP32 Wi-Fi 연결 테스트 시작");
  
  // Wi-Fi 연결 시작
  WiFi.begin(ssid, password);
  
  // Wi-Fi 연결 대기
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi 연결됨!");
  Serial.print("IP 주소: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 연결 상태 지속적으로 확인
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi 연결 상태 양호");
  } else {
    Serial.println("WiFi 연결 끊김");
  }
  delay(10000); // 10초마다 확인
}