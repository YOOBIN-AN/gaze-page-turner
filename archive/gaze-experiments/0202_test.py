# libcamera 사용
# pip install mediapipe opencv-python numpy
import cv2
import mediapipe as mp
import numpy as np

# Mediapipe 초기화
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [263, 249, 390, 373, 374, 380]

# libcamera-vid를 OpenCV에서 직접 읽기 위한 설정
cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

error_count = 0  # 오류 횟수 카운트 변수

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("프레임을 읽을 수 없습니다.")
        error_count += 1  # 오류 횟수 증가
        
        if error_count >= 10:  # 10번 이상 발생하면 종료
            print("카메라 입력 오류가 반복되어 프로그램을 종료합니다.")
            break
        continue

    error_count = 0  # 정상적으로 프레임을 읽으면 오류 횟수 초기화

'''
while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("프레임을 읽을 수 없습니다.")
        continue

    # 결과 출력
    cv2.imshow('Pupil Tracking', frame)

    # ESC 키로 종료
    if cv2.waitKey(1) & 0xFF == 27:
        break
'''

cap.release()
cv2.destroyAllWindows()
