[← 프로젝트 메인](../README.md)

# 초기 시선 인식 실험

파트를 나누기 전, 팀원이 함께 진행한 MediaPipe 기반 시선 인식 실험 코드입니다.  
최종 ① 시선 인식·트리거 코드는 이 실험을 바탕으로 조윤서님이 이어서 개발했으며, 이 저장소에는 포함하지 않았습니다.

&nbsp;

| 날짜 | 파일 | 내용 |
|---|---|---|
| 2025.01 | [`look_at_my_face.py`](gaze-experiments/look_at_my_face.py) | 웹캠 영상에 Face Mesh 얼굴 랜드마크 표시 |
| 2025.01 | [`look_at_my_eyes.py`](gaze-experiments/look_at_my_eyes.py) · [`catch_my_eyes.py`](gaze-experiments/catch_my_eyes.py) ~ [`catch_my_eyes3.py`](gaze-experiments/catch_my_eyes3.py) | 눈 영역 랜드마크 추출·표시 |
| 2025.02 | [`0202_test.py`](gaze-experiments/0202_test.py) | 라즈베리파이 카메라(libcamera)에서 동공 추적 |
| 2025.03 | [`0318.py`](gaze-experiments/0318.py) | 눈동자 랜드마크 인덱스로 동공 위치 표시 |
| 2025.03 | [`0318_sk.py`](gaze-experiments/0318_sk.py) | 머리 3D 자세(yaw·pitch·roll) 추정 |
| 2025.03 | [`catch_my_eyes4.py`](gaze-experiments/catch_my_eyes4.py) | 눈 랜드마크로 눈 중심 좌표 계산 |
| 2025.04 | [`0403_crop1.py`](gaze-experiments/0403_crop1.py) ~ [`0403_crop4.py`](gaze-experiments/0403_crop4.py) | 눈 영역을 잘라 확대하고 격자 위 상대 좌표로 표시 |
| 2025.04 | [`0403_timesleep1.py`](gaze-experiments/0403_timesleep1.py) ~ [`0403_timesleep3.py`](gaze-experiments/0403_timesleep3.py) | 좌·우 응시 게이지가 차면 알림음 재생 (트리거 판정의 초기 형태) |
