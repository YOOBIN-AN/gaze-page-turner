#include <ESP32Servo.h>
#include <WiFi.h>

// ===== WiFi 설정 =====
const char* ssid     = "YOUR_SSID";      // Wi-Fi 이름
const char* password = "YOUR_PASSWORD";  // Wi-Fi 비밀번호
WiFiServer server(8080);

// ===== 서보 객체 =====
Servo leftServo1, leftServo2, rightServo1, rightServo2;
Servo pageServo1, pageServo2;

// ===== 핀 번호 =====
const int leftServoPin1  = 16;
const int leftServoPin2  = 17;
const int rightServoPin1 = 21;
const int rightServoPin2 = 22;
const int pageServoPin1  = 25;
const int pageServoPin2  = 23;

// 상태
volatile bool isMoving = false;

static inline int clampDeg(int v){ return v<0?0:(v>180?180:v); }

// ===== 책 너비(cm) =====
float bookWidthCm = 40.0;   // 기본값, 라즈베리파이에서 갱신됨

// ===== 오프셋 및 카운터 =====
unsigned long leftTriggerCount=0, rightTriggerCount=0;

// BookHolding 목표/최종 각도 (수정된 초기값: 10/165)
float targetL2 = 8.0, targetR2 = 168.0;
float lastL2   = 8.0, lastR2   = 168.0;
float lastL1   = 0.0,  lastR1   = 180.0;   // 주 서보 최종값 저장

// ===== px → cm 변환 함수 =====
float pxToCm(float px) {
  return 39.0 + (px - 27.0) * (5.0 / 9.0);
}

// ===== 선형 보간 함수 =====
float mapWidthToAngle(float width, float x1, float y1, float x2, float y2) {
  return y1 + (width - x1) * (y2 - y1) / (x2 - x1);
}

// ===== 두께 보정 =====
void adjustTargetsOnLeftTrigger() {
  leftTriggerCount++;
  float diff = (int)((leftTriggerCount-rightTriggerCount)/3.0)*0.3;
  targetL2 = 8.0 - diff;   // 기준값 수정 반영
  targetR2 = 168.0 + diff;
}

void adjustTargetsOnRightTrigger() {
  rightTriggerCount++;
  float diff = (int)((rightTriggerCount-leftTriggerCount)/3.0)*0.3;
  targetL2 = 8.0 + diff;   // 기준값 수정 반영
  targetR2 = 168.0 - diff;
}

// ===== 부드럽게 움직이는 함수 (단일 서보) =====
void moveServoSlow(Servo &servo, float start, float end, int steps, int delayMs) {
  for (int i=0; i<=steps; i++) {
    float pos = start + (end - start) * i / steps;
    servo.write(clampDeg((int)pos));
    delay(delayMs);
  }
  servo.write(clampDeg((int)end));
}

// ===== 두 서보 동시 제어 함수 =====
void moveServosPair(Servo &servoA, float startA, float endA,
                    Servo &servoB, float startB, float endB,
                    int steps, int delayMs) {
  for (int i=0; i<=steps; i++) {
    float posA = startA + (endA - startA) * i / steps;
    float posB = startB + (endB - startB) * i / steps;
    servoA.write(clampDeg((int)posA));
    servoB.write(clampDeg((int)posB));
    delay(delayMs);
  }
  servoA.write(clampDeg((int)endA));
  servoB.write(clampDeg((int)endB));
}

// === 모든 서보 초기화 ===
void resetAllServos() {
  leftServo1.write(0);
  leftServo2.write(30);   // 초기 열린 상태
  rightServo1.write(180);
  rightServo2.write(150); // 초기 열린 상태
  pageServo1.write(90);
  pageServo2.write(0);
  delay(500);
}

// === Book Holding ===
void executeBookHolding() {
  Serial.println("[HOLD] start");

  // 1단계: L2(25→targetL2), R2(155→targetR2) 동시
  moveServosPair(leftServo2, 23, targetL2,
                 rightServo2,153,targetR2,
                 5, 200);
  delay(300);

  // 2단계: 책 너비 기반 L1/R1 이동
  float L1_max = mapWidthToAngle(bookWidthCm, 39,  60, 44, 90);
  float R1_max = mapWidthToAngle(bookWidthCm, 39, 120, 44, 90);

  moveServosPair(leftServo1, 0, L1_max,
                 rightServo1,180,R1_max,
                 15, 200);
  delay(300);

  // 최종 위치 저장
  lastL2=targetL2;
  lastR2=targetR2;
  lastL1=L1_max;
  lastR1=R1_max;

  Serial.print("[HOLD] done | L2=");
  Serial.print(lastL2,1);
  Serial.print(", R2=");
  Serial.print(lastR2,1);
  Serial.print(", L1=");
  Serial.print(lastL1,1);
  Serial.print(", R1=");
  Serial.print(lastR1,1);
  Serial.print(" | Width=");
  Serial.print(bookWidthCm,1);
  Serial.println("cm");
}

// === Release Book Holding (lastL1/lastR1 반영) ===
void releaseBookHolding() {
  Serial.println("[RELEASE] start");

  // 보조 서보 해제
  moveServosPair(leftServo2,lastL2,40,
                 rightServo2,lastR2,140,
                 5,200);
  delay(300);

  // 주 서보 해제
  moveServosPair(leftServo1,lastL1,120,
                 rightServo1,lastR1,60,
                 6,200);
  delay(300);

  Serial.println("[RELEASE] done");
}

// === 페이지 넘김 ===
void executePageTurnLeft() {
  Serial.println("[PAGE LEFT] start");

  pageServo1.write(180);
  pageServo2.write(0);
  delay(400);

  moveServoSlow(pageServo1, 180, 165,  3, 200);
  delay(200);
  moveServoSlow(pageServo2,   0,  35,  5, 200);
  delay(200);
  moveServoSlow(pageServo1, 165,   0, 15, 200);
  delay(200);
  moveServoSlow(pageServo2,  35,   0,  5, 200);
  delay(200);

  Serial.println("[PAGE LEFT] done");
}

void executePageTurnRight() {
  Serial.println("[PAGE RIGHT] start");

  pageServo1.write(0);
  pageServo2.write(0);
  delay(400);

  moveServoSlow(pageServo1,  0,  15,  3, 200);
  delay(200);
  moveServoSlow(pageServo2,  0,  35,  5, 200);
  delay(200);
  moveServoSlow(pageServo1, 15, 180, 15, 200);
  delay(200);
  moveServoSlow(pageServo2, 35,   0,  5, 200);
  delay(200);

  Serial.println("[PAGE RIGHT] done");
}

// === 출력 요약 ===
void printSummary(const char* direction) {
  Serial.print("[");
  Serial.print(direction);
  Serial.print("] count L=");
  Serial.print(leftTriggerCount);
  Serial.print(", R=");
  Serial.print(rightTriggerCount);
  Serial.print(" | targetL2=");
  Serial.print(targetL2,1);
  Serial.print(", targetR2=");
  Serial.print(targetR2,1);
  Serial.print(" | lastL1=");
  Serial.print(lastL1,1);
  Serial.print(", lastR1=");
  Serial.print(lastR1,1);
  Serial.print(" | Width=");
  Serial.print(bookWidthCm,1);
  Serial.println("cm");
}

// ===== 액션 함수 =====
void executeLeftAction() {
  if(isMoving){Serial.println("[BUSY]");return;}
  isMoving=true;
  adjustTargetsOnLeftTrigger();
  releaseBookHolding();
  executePageTurnLeft();
  executeBookHolding();
  printSummary("Left");
  isMoving=false;
}

void executeRightAction() {
  if(isMoving){Serial.println("[BUSY]");return;}
  isMoving=true;
  adjustTargetsOnRightTrigger();
  releaseBookHolding();
  executePageTurnRight();
  executeBookHolding();
  printSummary("Right");
  isMoving=false;
}

// ===== 아두이노 기본 구조 =====
void setup() {
  Serial.begin(115200);

  leftServo1.attach(leftServoPin1);
  leftServo2.attach(leftServoPin2);
  rightServo1.attach(rightServoPin1);
  rightServo2.attach(rightServoPin2);
  pageServo1.attach(pageServoPin1);
  pageServo2.attach(pageServoPin2);

  resetAllServos();

  // WiFi 연결
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    String cmd = client.readStringUntil('\n');
    cmd.trim();
    Serial.print("Received: "); Serial.println(cmd);

    if (cmd == "LEFT") {
      client.println("LEFT_ACTION_ACCEPTED");
      executeLeftAction();
    } 
    else if (cmd == "RIGHT") {
      client.println("RIGHT_ACTION_ACCEPTED");
      executeRightAction();
    } 
    else if (cmd == "RESET") {
      client.println("RESET_ACCEPTED");
      resetAllServos();
    } 
    else if (cmd.startsWith("PAGE_TURN_LEFT")) {
      int idx = cmd.indexOf("width=");
      if (idx > 0) {
        float px = cmd.substring(idx + 6).toFloat();
        if (px > 0) {
          bookWidthCm = pxToCm(px);
          Serial.print("Updated book width (cm): ");
          Serial.println(bookWidthCm,2);
        }
      }
      client.println("LEFT_ACTION_ACCEPTED");
      executeLeftAction();
    }
    else if (cmd.startsWith("PAGE_TURN_RIGHT")) {
      int idx = cmd.indexOf("width=");
      if (idx > 0) {
        float px = cmd.substring(idx + 6).toFloat();
        if (px > 0) {
          bookWidthCm = pxToCm(px);
          Serial.print("Updated book width (cm): ");
          Serial.println(bookWidthCm,2);
        }
      }
      client.println("RIGHT_ACTION_ACCEPTED");
      executeRightAction();
    }
    else {
      client.println("UNKNOWN_CMD");
    }
  }
}