#include <ESP32Servo.h>

// 서보 객체 생성 (왼쪽 모터)
Servo leftServo1;
Servo leftServo2;

// 서보 객체 생성 (오른쪽 모터)
Servo rightServo1;
Servo rightServo2;

//1번들: 120도 이동
//2번들: 45도 이동
// 핀 정의 (왼쪽 모터)
int leftServoPin1 = 16;  // 왼쪽 첫 번째 서보 PWM 핀
int leftServoPin2 = 17;  // 왼쪽 두 번째 서보 PWM 핀

// 핀 정의 (오른쪽 모터)
int rightServoPin1 = 21;  // 오른쪽 첫 번째 서보 PWM 핀
int rightServoPin2 = 22;  // 오른쪽 두 번째 서보 PWM 핀

void setup() {
  // 시리얼 통신 시작
  Serial.begin(115200);
  Serial.println("ESP32 Synchronized Dual Servo Control Starting...");
  
  // 왼쪽 서보 핀 할당
  leftServo1.attach(leftServoPin1, 500, 2400);
  leftServo2.attach(leftServoPin2, 500, 2400);
  
  // 오른쪽 서보 핀 할당
  rightServo1.attach(rightServoPin1, 500, 2400);
  rightServo2.attach(rightServoPin2, 500, 2400);
  
  // 초기 위치로 이동 (모두 0도에서 시작)
  leftServo1.write(0);
  leftServo2.write(0);
  rightServo1.write(0);
  rightServo2.write(0);
  delay(1000);
  
  Serial.println("All servos initialized at 0 degrees");
}

void loop() {

  // 1단계: 왼쪽 Servo1 (0->180도), 오른쪽 Servo1 (270->90도) 동시 실행
  Serial.println("Step 1: Left Servo1 (0->180), Right Servo1 (270->90) moving simultaneously");
  for (int i = 0; i <= 19; i++) {  // 19번 반복 (0도부터 180도까지 10도씩)
    int leftPos = 0 + (i * 10);    // 왼쪽: 0도에서 180도로
    int rightPos = 180 - (i * 10);  // 오른쪽: 360도에서 180도로
    
    leftServo1.write(leftPos);
    rightServo1.write(rightPos);
    
    Serial.print("Left Servo1: "); Serial.print(leftPos);
    Serial.print(", Right Servo1: "); Serial.println(rightPos);
    delay(200);
  }
  delay(500);
  
  // 2단계: 왼쪽 Servo2 (45->0도), 오른쪽 Servo2 (0->45도) 동시 실행
  Serial.println("Step 2: Left Servo2 (45->0), Right Servo2 (0->45) moving simultaneously");
  for (int i = 0; i <= 9; i++) {  // 10번 반복 (45도부터 0도까지 5도씩)
    int leftPos = 45 - (i * 5);   // 왼쪽: 45도에서 0도로
    int rightPos = 0 + (i * 5);   // 오른쪽: 0도에서 45도로
    
    leftServo2.write(leftPos);
    rightServo2.write(rightPos);
    
    Serial.print("Left Servo2: "); Serial.print(leftPos);
    Serial.print(", Right Servo2: "); Serial.println(rightPos);
    delay(200);
  }
  delay(500);
  
  // 3단계: 왼쪽 Servo1 (180->0도), 오른쪽 Servo1 (90->270도) 동시 실행
  Serial.println("Step 3: Left Servo1 (180->0), Right Servo1 (90->270) moving simultaneously");
  for (int i = 0; i <= 19; i++) {  // 19번 반복 (180도부터 0도까지 10도씩)
    int leftPos = 180 - (i * 10);  // 왼쪽: 180도에서 0도로
    int rightPos = 0 + (i * 10);  // 오른쪽: 180도에서 360도로
    
    leftServo1.write(leftPos);
    rightServo1.write(rightPos);
    
    Serial.print("Left Servo1: "); Serial.print(leftPos);
    Serial.print(", Right Servo1: "); Serial.println(rightPos);
    delay(200);
  }
  delay(500);
  
  // 4단계: 왼쪽 Servo2 (0->45도), 오른쪽 Servo2 (45->0도) 동시 실행
  Serial.println("Step 4: Left Servo2 (0->45), Right Servo2 (45->0) moving simultaneously");
  for (int i = 0; i <= 9; i++) {  // 10번 반복 (0도부터 45도까지 5도씩)
    int leftPos = 0 + (i * 5);    // 왼쪽: 0도에서 45도로
    int rightPos = 45 - (i * 5);  // 오른쪽: 45도에서 0도로
    
    leftServo2.write(leftPos);
    rightServo2.write(rightPos);
    
    Serial.print("Left Servo2: "); Serial.print(leftPos);
    Serial.print(", Right Servo2: "); Serial.println(rightPos);
    delay(200);
  }
  delay(1000);
  
  Serial.println("--- Cycle completed, repeating... ---\n");
}