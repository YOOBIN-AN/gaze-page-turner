#include <ESP32Servo.h>
#include <WiFi.h>

const char* ssid     = "YOUR_SSID";      // Wi-Fi 이름
const char* password = "YOUR_PASSWORD";  // Wi-Fi 비밀번호
WiFiServer server(8080);

// ===== 서보 객체 =====
Servo leftServo1;
Servo leftServo2;
Servo rightServo1;
Servo rightServo2;
Servo pageServo1;
Servo pageServo2;

// ===== 핀맵 =====
const int leftServoPin1  = 16;
const int leftServoPin2  = 17;
const int rightServoPin1 = 21;
const int rightServoPin2 = 22;
const int pageServoPin1  = 18;
const int pageServoPin2  = 19;

// 상태
volatile bool isMoving = false;

// 보드 LED
#define STATUS_LED 2

// 앞으로 정의될 함수들을 미리 선언
void executeLeftAction();
void executeRightAction();
void resetAllServos();

// ===== 즉시 응답용 큐 =====
enum Cmd { CMD_NONE, CMD_LEFT, CMD_RIGHT, CMD_RESET };
volatile Cmd pendingCmd = CMD_NONE;

// ===== 응답 먼저 보내는 함수 =====
void handleRequestAndAck(const String& request, WiFiClient& client) {
  String response = "UNKNOWN_COMMAND";

  if (request == "STATUS") {
    response = isMoving ? "MOVING" : "READY";
  } else if (request == "PAGE_TURN_LEFT") {
    if (isMoving || pendingCmd != CMD_NONE) response = "BUSY";
    else { pendingCmd = CMD_LEFT; response = "LEFT_ACTION_ACCEPTED"; }
  } else if (request == "PAGE_TURN_RIGHT") {
    if (isMoving || pendingCmd != CMD_NONE) response = "BUSY";
    else { pendingCmd = CMD_RIGHT; response = "RIGHT_ACTION_ACCEPTED"; }
  } else if (request == "RESET") {
    if (isMoving || pendingCmd != CMD_NONE) response = "BUSY";
    else { pendingCmd = CMD_RESET; response = "RESET_ACCEPTED"; }
  } else if (request.length() == 0) {
    response = "EMPTY";
  }

  client.print(response + "\n");   // ★ 응답 즉시 전송
  client.stop();
  Serial.print("[RESP] "); Serial.println(response);
}

void processPending() {
  if (isMoving || pendingCmd == CMD_NONE) return;
  Cmd c = pendingCmd; pendingCmd = CMD_NONE;

  if (c == CMD_LEFT)       executeLeftAction();
  else if (c == CMD_RIGHT) executeRightAction();
  else if (c == CMD_RESET) { resetAllServos(); isMoving = false; }
}

// ===== 유틸 =====
static inline int clampDeg(int v){ return v < 0 ? 0 : (v > 180 ? 180 : v); }

// ===== 서보 초기화 =====
void resetAllServos() {
  leftServo1.write(0);
  leftServo2.write(0);
  rightServo1.write(180);
  rightServo2.write(180);
  pageServo1.write(0);
  pageServo2.write(0);
  delay(500);
}

void moveServoSlow(Servo &servo, int startAngle, int endAngle, int stepSize = 10, int delayTime = 100) {
  startAngle = clampDeg(startAngle);
  endAngle   = clampDeg(endAngle);
  stepSize   = abs(stepSize);
  if (startAngle < endAngle) {
    for (int a = startAngle; a <= endAngle; a += stepSize) { servo.write(a); delay(delayTime); }
    servo.write(endAngle);
  } else {
    for (int a = startAngle; a >= endAngle; a -= stepSize) { servo.write(a); delay(delayTime); }
    servo.write(endAngle);
  }
}

// === 동작 시퀀스 ===
void executeBookHolding() {
  Serial.println("[HOLD] start");

  // 1단계: L2 0->15, R2 180->165 (동시)
  for (int i = 0; i <= 5; i++) {
    int leftPos  = clampDeg(0   + i * 3);
    int rightPos = clampDeg(180 - i * 3);
    leftServo2.write(leftPos);
    rightServo2.write(rightPos);
    delay(200);
  }
  delay(300);

  // 2단계: L1 0->120, R1 180->60 (동시)
  for (int i = 0; i <= 12; i++) {
    int leftPos  = clampDeg(0   + i * 10);
    int rightPos = clampDeg(180 - i * 10);
    leftServo1.write(leftPos);
    rightServo1.write(rightPos);
    delay(200);
  }
  delay(300);

  Serial.println("[HOLD] done");
}

void releaseBookHolding() {
  Serial.println("[RELEASE] start");

  // 1단계: L2 15->0, R2 165->180 (동시)
  for (int i = 0; i <= 5; i++) {
    int leftPos  = clampDeg(15  - i * 3);
    int rightPos = clampDeg(165 + i * 3);
    leftServo2.write(leftPos);
    rightServo2.write(rightPos);
    delay(200);
  }
  delay(300);

  // 2단계: L1 120->0, R1 60->180 (동시)
  for (int i = 0; i <= 12; i++) {
    int leftPos  = clampDeg(180 - i * 10);
    int rightPos = clampDeg(0   + i * 10);
    leftServo1.write(leftPos);
    rightServo1.write(rightPos);
    delay(200);
  }
  delay(300);
  
  Serial.println("[RELEASE] done");
}

// 왼쪽 페이지(우->좌) 넘김
void executePageTurnLeft() {
  Serial.println("[PAGE LEFT] start");

  pageServo1.write(180);
  pageServo2.write(45);
  delay(400);

  moveServoSlow(pageServo1, 180, 125,  10, 80);
  delay(200);
  moveServoSlow(pageServo2,  45,   0,  10, 80);
  delay(200);
  moveServoSlow(pageServo1, 125,  35,  10, 80);
  delay(200);
  moveServoSlow(pageServo2,   0,  45,  10, 80);
  delay(200);
  moveServoSlow(pageServo1,  35,   0,  10, 80);
  delay(200);
  // 복귀
  moveServoSlow(pageServo1, 0, 180, 10, 80);

  Serial.println("[PAGE LEFT] done");
}

// 오른쪽 페이지(좌->우) 넘김
void executePageTurnRight() {
  Serial.println("[PAGE RIGHT] start");

  pageServo1.write(0);
  pageServo2.write(0);
  delay(400);

  moveServoSlow(pageServo1, 0,   30,  10, 80);
  delay(200);
  moveServoSlow(pageServo2, 0,   45,  10, 80);
  delay(200);
  moveServoSlow(pageServo1, 30,  125, 10, 80);
  delay(200);
  moveServoSlow(pageServo2, 45,  0,   10, 80);
  delay(200);
  moveServoSlow(pageServo1, 125, 180, 10, 80);
  delay(200);
  // 복귀
  moveServoSlow(pageServo1, 180, 0,   10, 80);

  Serial.println("[PAGE RIGHT] done");
}

void executeLeftAction() {
  if (isMoving) { Serial.println("[BUSY]"); return; }
  isMoving = true;
  releaseBookHolding();
  executePageTurnLeft();
  executeBookHolding();
  isMoving = false;
}

void executeRightAction() {
  if (isMoving) { Serial.println("[BUSY]"); return; }
  isMoving = true;
  releaseBookHolding();
  executePageTurnRight();
  executeBookHolding();
  isMoving = false;
}

// ===== setup =====
void setup() {
  Serial.begin(115200);
  pinMode(STATUS_LED, OUTPUT);
  digitalWrite(STATUS_LED, LOW);

  Serial.println("\n[BOOT] ESP32 Page Turner");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("[WiFi] connecting");
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }
  digitalWrite(STATUS_LED, HIGH);
  Serial.print("\n[WiFi] connected: ");
  Serial.println(WiFi.localIP());

  server.begin();
  Serial.println("[Server] listening on 8080");

  leftServo1.attach(leftServoPin1, 500, 2400);
  leftServo2.attach(leftServoPin2, 500, 2400);
  rightServo1.attach(rightServoPin1, 500, 2400);
  rightServo2.attach(rightServoPin2, 500, 2400);
  pageServo1.attach(pageServoPin1, 500, 2400);
  pageServo2.attach(pageServoPin2, 500, 2400);

  resetAllServos();
  Serial.println("[Init] servos ready");
}

// ===== loop =====
void loop() {
  WiFiClient client = server.available();
  if (!client) {
    processPending();
    delay(5);
    return;
  }

  Serial.println("[Client] connected");
  String request;
  unsigned long t0 = millis();

  while (client.connected() && millis() - t0 < 3000UL) {
    if (client.available()) {
      request = client.readStringUntil('\n');
      request.trim();
      break;
    }
    delay(1);
  }

  Serial.print("[REQ] "); Serial.println(request);

  // 응답 먼저 보내고 동작은 큐에 적재
  handleRequestAndAck(request, client);

  // 바로 실행 시작해도 됨
  processPending();
}
