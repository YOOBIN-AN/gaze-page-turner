void setup() {
  Serial.begin(115200);
  pinMode(5, OUTPUT);  // Lolin D32의 온보드 LED 핀
  Serial.println("ESP32 Lolin D32 테스트 시작!");
}

void loop() {
  digitalWrite(5, HIGH);  // LED 켜기
  Serial.println("LED ON");
  delay(1000);
  digitalWrite(5, LOW);   // LED 끄기
  Serial.println("LED OFF");
  delay(1000);
}