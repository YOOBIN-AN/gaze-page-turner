# firmware

ESP32 (LOLIN D32) 서보 제어 코드 — Arduino IDE

- Raspberry Pi로부터 Wi-Fi 소켓으로 넘김 방향 명령 수신
- MG90S 넘김 팔 · MG946R 고정 팔 PWM 제어
- 고정 해제 → 넘김 → 재고정 시퀀스, 넘김 누적 횟수 기반 각도 보정
