[← 책장 구동부](../README.md)

# archive

최종 펌웨어([`servo_final.ino`](../firmware/servo_final/servo_final.ino))에 이르기까지의 ESP32 테스트 코드와 이전 3D 모델입니다.  
코드의 Wi-Fi 이름 · 비밀번호는 `YOUR_SSID` · `YOUR_PASSWORD`로 바꿔 두었습니다.

### 1단계 · 보드와 서보 단독 테스트

LOLIN D32 보드 → Wi-Fi 연결 → 서보 1개 PWM 제어

| 날짜 | 파일 | 내용 |
|---|---|---|
| 2025.05.16 | [`initial_test.ino`](firmware/initial_test.ino) | LOLIN D32 온보드 LED 점멸로 보드 동작 확인 |
| 2025.05.16 | [`wifi_connection.ino`](firmware/wifi_connection.ino) | ESP32 Wi-Fi 연결 테스트 |
| 2025.05.22 | [`servo_test.ino`](firmware/servo_test.ino) | MG946R 1개를 0° · 90° · 180°로 반복 이동 (LEDC PWM 직접 제어) |

### 2단계 · 라즈베리파이 통신과 고정 팔 동작

소켓 · HTTP 통신 → 고정 팔 4축 → 해제 · 넘김 · 재고정 시퀀스

| 날짜 | 파일 | 내용 |
|---|---|---|
| 2025.08.19 | [`ip_findout.ino`](firmware/ip_findout.ino) | ESP32 IP 확인 · 연결 상태 주기 출력 |
| 2025.08.19 | [`raspberry_communication.ino`](firmware/raspberry_communication.ino) | HTTP 서버로 라즈베리파이 접속 확인 |
| 2025.08.19 | [`8080_open.ino`](firmware/8080_open.ino) | 8080 포트 소켓 서버, `PAGE_TURN_LEFT` · `RIGHT` 명령 수신 틀 |
| 2025.08.20 | [`pin_code.ino`](firmware/pin_code.ino) | 고정 팔 서보 4개 핀 할당 · 좌우 동시 동작 |
| 2025.08.27 | [`servo_final_2.ino`](firmware/servo_final_2.ino) | 소켓 명령 → 고정 해제 · 넘김 · 재고정 시퀀스 (각도 보정 전) |
| 2025.08.29 | [`communication_code.ino`](firmware/communication_code.ino) | HTTP 요청으로 LED 켜기 · 끄기 (통신 확인용) |
| 2025.08.29 | [`bridge_code.ino`](firmware/bridge_code.ino) | HTTP POST(JSON)로 서보 2개 각도 지정 |

[`servo_final.ino`](../firmware/servo_final/servo_final.ino)(2025.08.29)에서 책 너비 · 두께 보정을 더해 최종본이 되었습니다.

### 이전 3D 모델

| 날짜 | 파일 | 내용 |
|---|---|---|
| 2025.07.30 | [`servo_case_pair_v1.stl`](models/servo_case_pair_v1.stl) | 고정 팔 서보 케이스 이전 버전 (최종본은 [`models/`](../models/)) |
