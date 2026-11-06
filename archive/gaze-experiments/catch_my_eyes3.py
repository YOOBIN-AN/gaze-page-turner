import cv2
import mediapipe as mp
import numpy as np  # NumPy 임포트 추가

# Mediapipe Face Mesh 초기화
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
drawing_utils = mp.solutions.drawing_utils

# 웹캠 열기
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("카메라에서 영상을 읽을 수 없습니다.")
        break

    # BGR을 RGB로 변환
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Mediapipe로 처리
    result = face_mesh.process(rgb_frame)

    # 얼굴 랜드마크 추출 및 눈 영역만 그리기
    if result.multi_face_landmarks:
        for landmarks in result.multi_face_landmarks:
            # 눈 테두리 인덱스 (왼쪽 눈 33~133, 오른쪽 눈 362~463)
            left_eye_indices = list(range(33, 133))
            right_eye_indices = list(range(362, 463))

            # 왼쪽 눈과 오른쪽 눈의 좌표 추출
            left_eye_landmarks = [landmarks.landmark[i] for i in left_eye_indices]
            right_eye_landmarks = [landmarks.landmark[i] for i in right_eye_indices]

            # 좌표 평균을 통해 눈동자 중심 계산
            def calculate_eye_center(eye_landmarks):
                x = sum([landmark.x for landmark in eye_landmarks]) / len(eye_landmarks)
                y = sum([landmark.y for landmark in eye_landmarks]) / len(eye_landmarks)
                center_x = int(x * frame.shape[1])
                center_y = int(y * frame.shape[0])
                return center_x, center_y

            # 왼쪽, 오른쪽 눈동자 중심 계산
            left_eye_center = calculate_eye_center(left_eye_landmarks)
            right_eye_center = calculate_eye_center(right_eye_landmarks)

            # 눈 테두리 그리기 (왼쪽, 오른쪽 눈)
            left_eye_points = [(int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])) for landmark in left_eye_landmarks]
            right_eye_points = [(int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])) for landmark in right_eye_landmarks]
            cv2.polylines(frame, [np.array(left_eye_points, np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)  # 왼쪽 눈 테두리
            cv2.polylines(frame, [np.array(right_eye_points, np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)  # 오른쪽 눈 테두리

            # 눈 중심 그리기 (동공)
            cv2.circle(frame, left_eye_center, 5, (0, 255, 0), -1)  # 왼쪽 눈동자
            cv2.circle(frame, right_eye_center, 5, (0, 255, 0), -1)  # 오른쪽 눈동자

            # 눈 테두리 점 그리기
            for i in left_eye_indices:
                x = int(landmarks.landmark[i].x * frame.shape[1])
                y = int(landmarks.landmark[i].y * frame.shape[0])
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)  # 왼쪽 눈 랜드마크
            for i in right_eye_indices:
                x = int(landmarks.landmark[i].x * frame.shape[1])
                y = int(landmarks.landmark[i].y * frame.shape[0])
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)  # 오른쪽 눈 랜드마크

    # 화면에 출력
    cv2.imshow("Eye Tracking with Eye Contour and Pupil", frame)

    # 'q'를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()