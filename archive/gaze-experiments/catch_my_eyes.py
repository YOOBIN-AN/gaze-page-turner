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
            # 왼쪽 눈 (33~133번 랜드마크)
            left_eye_landmarks = []
            for i in range(33, 134):
                left_eye_landmarks.append(landmarks.landmark[i])

            # 오른쪽 눈 (362~463번 랜드마크)
            right_eye_landmarks = []
            for i in range(362, 464):
                right_eye_landmarks.append(landmarks.landmark[i])

            # 눈의 중심 계산 (좌표의 평균값)
            def calculate_eye_center(eye_landmarks):
                x = 0
                y = 0
                for landmark in eye_landmarks:
                    x += landmark.x
                    y += landmark.y
                return int((x / len(eye_landmarks)) * frame.shape[1]), int((y / len(eye_landmarks)) * frame.shape[0])

            left_eye_center = calculate_eye_center(left_eye_landmarks)
            right_eye_center = calculate_eye_center(right_eye_landmarks)

            # 눈 중심 그리기 (눈만 따로 그리기)
            cv2.circle(frame, left_eye_center, 5, (0, 255, 0), -1)  # 왼쪽 눈동자
            cv2.circle(frame, right_eye_center, 5, (0, 255, 0), -1)  # 오른쪽 눈동자

            # 눈 랜드마크 그리기 (세밀하게)
            for landmark in left_eye_landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)  # 왼쪽 눈 랜드마크
            for landmark in right_eye_landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)  # 오른쪽 눈 랜드마크

    # 화면에 출력
    cv2.imshow("Eye Tracking with Detailed Landmarks", frame)

    # 'q'를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()