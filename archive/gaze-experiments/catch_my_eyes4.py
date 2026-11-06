
import cv2
import mediapipe as mp

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
            # 눈의 랜드마크 범위 설정 (눈의 윤곽에 맞는 더 많은 랜드마크 사용)
            left_eye_indices = [33, 133, 160, 159, 158, 145, 144, 163]  # 왼쪽 눈
            right_eye_indices = [362, 463, 387, 386, 385, 374, 373, 380]  # 오른쪽 눈

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

            # 눈 테두리 따라 작은 점 그리기
            for i in left_eye_indices:
                x = int(landmarks.landmark[i].x * frame.shape[1])
                y = int(landmarks.landmark[i].y * frame.shape[0])
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)  # 왼쪽 눈 테두리 작은 점
            for i in right_eye_indices:
                x = int(landmarks.landmark[i].x * frame.shape[1])
                y = int(landmarks.landmark[i].y * frame.shape[0])
                cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)  # 오른쪽 눈 테두리 작은 점

            # 눈동자 중심에 큰 점 그리기
            cv2.circle(frame, left_eye_center, 10, (0, 0, 255), -1)  # 왼쪽 눈동자 중심 큰 점
            cv2.circle(frame, right_eye_center, 10, (0, 0, 255), -1)  # 오른쪽 눈동자 중심 큰 점

    # 화면에 출력
    cv2.imshow("Eye Tracking with Accurate Landmarks", frame)

    # 'q'를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

