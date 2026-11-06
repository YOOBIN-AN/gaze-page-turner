int servoPin = 18;

void setup() {
  Serial.begin(115200);
  
  // PWM 설정
  ledcAttach(servoPin, 50, 16);  // 50Hz, 16bit 해상도
  
  Serial.println("MG946R Simple Position Test");
  Serial.println("===========================");
  
  delay(1000);
}

void loop() {
  // 0도
  Serial.println("Position: 0 degrees");
  setServoAngle(0);
  delay(3000);  // 3초 대기
  
  // 90도
  Serial.println("Position: 90 degrees");
  setServoAngle(90);
  delay(3000);  // 3초 대기
  
  // 180도
  Serial.println("Position: 180 degrees");
  setServoAngle(180);
  delay(3000);  // 3초 대기
  
  Serial.println("Cycle completed, repeating...");
  Serial.println("-----------------------------");
}

void setServoAngle(int angle) {
  // MG946R을 위한 PWM 설정
  int pulseWidth = map(angle, 0, 180, 500, 2500);
  int dutyCycle = (pulseWidth * 65536) / 20000;
  
  ledcWrite(servoPin, dutyCycle);
}