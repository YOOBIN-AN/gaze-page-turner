#include <WiFi.h>
#include <WebServer.h>

// WiFi 설정
const char* ssid = "YOUR_SSID";      // Wi-Fi 이름
const char* password = "YOUR_PASSWORD";  // Wi-Fi 비밀번호

// 웹 서버 설정 (포트 80)
WebServer server(80);

// LED 제어 핀 설정
#define LED_PIN 5

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  
  // WiFi 연결
  Serial.print("WiFi 연결 중...");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi 연결됨!");
  Serial.print("IP 주소: ");
  Serial.println(WiFi.localIP());
  
  // 라우팅 설정
  server.on("/", handleRoot);
  server.on("/led/on", handleLedOn);
  server.on("/led/off", handleLedOff);
  server.on("/status", handleStatus);
  
  // 서버 시작
  server.begin();
  Serial.println("HTTP 서버 시작됨");
}

void loop() {
  server.handleClient();
  delay(10);
}

// 루트 페이지
void handleRoot() {
  String html = "<html><body>";
  html += "<h1>ESP32 - 라즈베리파이 통신 테스트</h1>";
  html += "<p><a href='/led/on'><button>LED 켜기</button></a></p>";
  html += "<p><a href='/led/off'><button>LED 끄기</button></a></p>";
  html += "<p><a href='/status'><button>상태 확인</button></a></p>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

// LED 켜기
void handleLedOn() {
  digitalWrite(LED_PIN, HIGH);
  server.sendHeader("Location", "/");
  server.send(303);
}

// LED 끄기
void handleLedOff() {
  digitalWrite(LED_PIN, LOW);
  server.sendHeader("Location", "/");
  server.send(303);
}

// 상태 정보 (JSON 형식)
void handleStatus() {
  String json = "{";
  json += "\"led_status\":\"" + String(digitalRead(LED_PIN) ? "on" : "off") + "\",";
  json += "\"uptime\":\"" + String(millis() / 1000) + "\",";
  json += "\"free_heap\":\"" + String(ESP.getFreeHeap()) + "\"";
  json += "}";
  
  server.send(200, "application/json", json);
}