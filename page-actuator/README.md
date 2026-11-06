[← 프로젝트 메인](../README.md)

# ② 책장 구동부
**Page Actuator** · 시선 추적 책장 넘김 장치 중 담당 파트

> 시선 트리거 명령을 받아 서보모터로 책장을 넘기고, 넘긴 페이지가 되돌아오지 않도록 양쪽에서 눌러 고정하는 장치

![ESP32](https://img.shields.io/badge/ESP32-E7352C?style=flat-square&logo=espressif&logoColor=white)
![Arduino](https://img.shields.io/badge/Arduino-00878F?style=flat-square&logo=arduino&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=flat-square&logo=cplusplus&logoColor=white)
![Tinkercad](https://img.shields.io/badge/Tinkercad-1477D1?style=flat-square&logo=tinkercad&logoColor=white)

<p>
<img src="docs/images/page_turning.png" width="49%">
<img src="docs/images/page_holding.png" width="49%">
</p>
<sub>왼쪽: MG90S 넘김 팔이 오른쪽 페이지를 넘기는 모습 / 오른쪽: MG946R 고정 팔이 양쪽 페이지를 눌러 정리하는 모습</sub>

&nbsp;

<a id="목차"></a>**목차** · [개요](#1-개요) · [데모](#2-데모) · [동작 원리](#3-동작-원리) · [기구 설계](#4-기구-설계) · [트러블슈팅](#5-트러블슈팅) · [한계 및 개선 방향](#6-한계-및-개선-방향) · [폴더 구조](#7-폴더-구조)

&nbsp;

## 1. 개요

한이음 드림업 프로젝트에서 ② 책장 구동부를 맡아 서보모터 제어와 3D 모델링을 담당했습니다.  
시선 파트가 보낸 트리거 명령 하나를 고정 해제 → 넘김 → 재고정의 물리 동작으로 바꾸고, 책 크기와 두께에 맞춰 모터 각도를 보정합니다.

| | 기존 물리 독서 보조기구 | 이 장치 |
|---|---|---|
| **조작** | 리모컨 · 버튼 (손 사용 필요) | 시선 트리거 명령 (Wi-Fi) |
| **구조** | 크고 복잡해 휴대성이 낮음 | 기존 독서대에 붙이는 3D 프린팅 모듈 |
| **책 대응** | — | 책 너비 · 넘김 횟수로 모터 각도 보정 |

<sub>[↑ 목차](#목차)</sub>

&nbsp;

## 2. 데모

### 오른쪽 넘김

<!-- 영상: demo_turn_right.mp4 -->

<sub>고정 팔 해제 → 넘김 팔이 오른쪽 페이지를 넘김 → 고정 팔이 양쪽 페이지를 다시 눌러 정리</sub>

&nbsp;

### 왼쪽 넘김

<!-- 영상: demo_turn_left.mp4 -->

<sub>반대쪽 트리거도 같은 순서로 동작 — 넘김 팔 좌 · 우 대칭 구동</sub>

&nbsp;

### 다양한 크기의 책

<!-- 영상: demo_book_sizes.mp4 -->

<sub>너비가 다른 두 책에서 같은 장치로 넘김 · 고정</sub>

&nbsp;

### 결과 요약

| 기능 | 결과 |
|---|---|
| 자동 책장 넘김 | 좌 · 우 트리거 모두 넘김 팔이 한 장씩 넘긴 뒤 안전 위치로 복귀 |
| 책 고정 · 정리 | 넘김 전 고정 해제, 넘김 후 양쪽 페이지를 눌러 평탄화 · 되말림 방지 |
| 책 너비 보정 | 너비가 다른 책에서 고정 팔 하단 모터 각도를 바꿔 같은 동작 수행 |
| 두께 보정 | 넘김 횟수가 늘수록 고정 팔 상단 모터 목표 각도가 바뀌는 것을 시리얼 로그로 확인 |

<sub>[↑ 목차](#목차)</sub>

&nbsp;

## 3. 동작 원리

### 처리 흐름

```mermaid
flowchart TD
    T["트리거 명령 수신<br/>Raspberry Pi → ESP32 (Wi-Fi 소켓)"] --> C["두께 보정<br/>좌 · 우 넘김 횟수 누적<br/>→ 상단 모터 목표 각도"]
    C --> R["고정 해제<br/>RELEASE"]
    R --> P["책장 넘김<br/>PAGE LEFT · RIGHT"]
    P --> H["재고정<br/>HOLD"]
    H --> L["기록 출력<br/>시리얼 로그"]
    L --> W["안전 위치 복귀<br/>다음 트리거 대기"]

    classDef io fill:#57606a,stroke:#57606a,color:#fff
    classDef step fill:#f6f8fa,stroke:#d0d7de,color:#24292f
    class T,W io
    class C,R,P,H,L step
```

넘기기 전에 고정을 먼저 풀어, 고정 팔이 넘어가는 페이지를 붙잡지 않도록 순서를 정했습니다.

<details>
<summary><b>하드웨어 구성</b></summary>
<br>

```mermaid
flowchart LR
    PW["12V 어댑터<br/>+ 전원 스위치"] --> DC1["DC-DC 컨버터<br/>5V"]
    PW --> DC2["DC-DC 컨버터<br/>6V"]
    DC1 --> RPI["Raspberry Pi<br/>시선 추적 · 트리거"]
    DC1 --> ESP["ESP32 (LOLIN D32)<br/>PWM 생성"]
    RPI <-- Wi-Fi --> ESP
    ESP -- PWM --> S1["MG90S × 2<br/>넘김 팔"]
    ESP -- PWM --> S2["MG946R × 2<br/>왼쪽 고정 팔"]
    ESP -- PWM --> S3["MG946R × 2<br/>오른쪽 고정 팔"]
    DC2 --> S1
    DC2 --> S2
    DC2 --> S3

    classDef io fill:#57606a,stroke:#57606a,color:#fff
    classDef step fill:#f6f8fa,stroke:#d0d7de,color:#24292f
    class PW io
    class DC1,DC2,RPI,ESP,S1,S2,S3 step
```

| 부품 | 역할 |
|---|---|
| MG90S × 2 | 토크가 작은 소형 서보 — 넘김 팔을 와이퍼처럼 움직여 페이지를 넘김 |
| MG946R × 4 | 토크가 큰 서보 — 좌 · 우 고정 팔을 상단 · 하단 2축으로 움직여 페이지를 누름 |
| DC-DC 컨버터 | 12V를 Raspberry Pi · ESP32용 5V와 서보용 6V로 나눠 공급 |

<p>
<img src="docs/images/page_turn_arm.jpg" width="40%">
<img src="docs/images/hold_arm.jpg" width="43%">
</p>
<sub>왼쪽: MG90S 넘김 팔과 3D 프린팅 거치대 / 오른쪽: MG946R 고정 팔</sub>

</details>

&nbsp;

### 각도 보정 규칙

```mermaid
flowchart LR
    A["캘리브레이션<br/>책 좌 · 우 하단 응시"] --> B["책 너비<br/>px → cm 환산"] --> C["선형 보간<br/>미리 측정한 두 책 기준"] --> D["고정 팔<br/>하단 모터 각도"]
    E["트리거 방향<br/>LEFT · RIGHT"] --> F["좌 · 우 넘김 횟수<br/>각각 누적"] --> G["두께 변화 반영"] --> H["고정 팔<br/>상단 모터 각도"]

    classDef ask fill:#f6f8fa,stroke:#57606a,color:#24292f
    classDef out fill:#fff8c5,stroke:#d4a72c,color:#4d2d00
    class A,B,C,E,F,G ask
    class D,H out
```

책이 넓을수록 고정 팔이 더 바깥쪽을 누르고, 한쪽으로 넘길수록 두꺼워지는 쪽과 얇아지는 쪽에 맞춰 누르는 각도를 조금씩 바꿉니다.

<details>
<summary><b>시리얼 로그로 본 두께 보정</b></summary>
<br>

<img src="docs/images/serial_log.png" width="55%">

| 오른쪽 넘김 횟수 | 왼쪽 상단 모터 (`targetL2`) | 오른쪽 상단 모터 (`targetR2`) |
|:-:|:-:|:-:|
| 2회 | 15.0 | 165.0 |
| 3회 | 15.3 | 164.7 |

오른쪽으로 넘길수록 왼쪽 페이지는 두꺼워지고 오른쪽 페이지는 얇아져, 두 상단 모터의 목표 각도가 반대 방향으로 조금씩 바뀝니다.

</details>

<sub>[↑ 목차](#목차)</sub>

&nbsp;

## 4. 기구 설계

### 고정 팔 서보 케이스

<p>
<img src="docs/images/servo_case_left.png" width="35%">
<img src="docs/images/servo_case_right.png" width="35%">
</p>
<sub>왼쪽 · 오른쪽 고정 팔 서보 케이스 — MG946R 상단 · 하단 2축을 한 케이스에 결합 (Tinkercad)</sub>

&nbsp;

### 넘김 팔 거치대

<p>
<img src="docs/images/page_arm_mount_a.png" width="45%">
<img src="docs/images/page_arm_mount_b.png" width="45%">
</p>
<sub>독서대 하단에 부착해 MG90S와 쇠 막대를 고정하는 부품</sub>

&nbsp;

- 서보모터 · 카메라 장착용 거치대를 Tinkercad로 설계하고 3D 프린팅
- 프린팅 후 실제 독서대에 부착해 각도 · 위치를 맞추며 반복 수정
- 넘김 팔 끝에는 고무 마개를 씌워 종이와의 마찰 확보
- 서보 케이스 모델 → [`models/`](models/) (GitHub에서 STL 파일을 열면 3D로 볼 수 있습니다)

<sub>[↑ 목차](#목차)</sub>

&nbsp;

## 5. 트러블슈팅

| # | 문제 | 해결 |
|:-:|---|---|
| 1 | 책이 끝까지 넘어가지 않거나 고정이 풀림 | 서보 부착 방향 · 각도를 반복 테스트로 조정, 넘김 팔 좌 · 우 대칭 동작 |
| 2 | 넘길수록 고정이 불안정해짐 | 좌 · 우 넘김 횟수를 누적해 상단 모터 각도 보정 |
| 3 | 독서대 뒷면 배선 간섭 · 단선 | 부품 배치와 선 경로를 다시 설계, 납땜 연결부 보강 |

<details>
<summary><b>원인 자세히 보기</b></summary>
<br>

| # | 원인 |
|:-:|---|
| 1 | 각도가 너무 크거나 작으면 페이지를 끝까지 넘기지 못하거나 누르는 힘이 부족함 |
| 2 | 한쪽으로 넘길수록 좌 · 우 페이지 두께가 달라져 같은 각도로는 누르는 위치가 달라짐 |
| 3 | 점퍼선으로 부품을 연결하면서 독서대 뒷면에 장치가 모여 선끼리 간섭 |

</details>

<sub>[↑ 목차](#목차)</sub>

&nbsp;

## 6. 한계 및 개선 방향

**한계**

- 각도가 경험적 값이라 종이 재질 · 제본 방식이 다른 책에서는 재조정이 필요함
- 책 너비 보정이 두 기준 책 사이의 선형 보간이라, 그 범위를 벗어난 크기의 책에서는 오차가 생김
- 페이지가 실제로 넘어갔는지 확인하지 않고 정해진 순서대로만 동작

**개선 방향**

- 카메라로 넘김 성공 여부를 확인해 실패 시 다시 넘기는 피드백 제어
- 다양한 책에서 각도 데이터를 모아 보정식 정교화
- 전용 PCB · 일체형 케이스로 배선 정리 및 휴대성 개선

<sub>[↑ 목차](#목차)</sub>

&nbsp;

## 7. 폴더 구조

<pre>
page-actuator/
├── <a href="README.md">README.md</a>
├── <a href="models/">models/</a>
│   ├── <a href="models/servo_case_left.stl">servo_case_left.stl</a>               왼쪽 고정 팔 서보 케이스
│   ├── <a href="models/servo_case_right.stl">servo_case_right.stl</a>              오른쪽 고정 팔 서보 케이스
│   └── <a href="models/servo_case_pair.stl">servo_case_pair.stl</a>               왼쪽 + 오른쪽 한 파일
└── <a href="docs/images/">docs/images/</a>                          README 이미지
</pre>

<sub>[↑ 목차](#목차)</sub>
