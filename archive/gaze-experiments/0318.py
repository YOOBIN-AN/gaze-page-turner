import cv2
import mediapipe as mp

# MediaPipe Face Mesh 초기화
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# 웹캠(라즈베리파이 IR 카메라 사용 시: 0 또는 1로 변경)
cap = cv2.VideoCapture(0)

# 눈동자 인덱스 (MediaPipe 기준)
LEFT_IRIS = [474, 475, 476, 477]  # 왼쪽 눈 홍채
RIGHT_IRIS = [469, 470, 471, 472]  # 오른쪽 눈 홍채

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("프레임을 가져올 수 없습니다.")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb_frame)

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            height, width, _ = frame.shape

            # 얼굴 전체 랜드마크 그리기
            for idx, lm in enumerate(face_landmarks.landmark):
                x, y = int(lm.x * width), int(lm.y * height)
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)  # 초록색 점

            # 홍채(눈동자) 추적
            left_iris = []
            right_iris = []

            for idx in LEFT_IRIS:
                lm = face_landmarks.landmark[idx]
                x, y = int(lm.x * width), int(lm.y * height)
                left_iris.append((x, y))
                cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)  # 파란색 점

            for idx in RIGHT_IRIS:
                lm = face_landmarks.landmark[idx]
                x, y = int(lm.x * width), int(lm.y * height)
                right_iris.append((x, y))
                cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)  # 빨간색 점

            # 홍채 중심 좌표 계산
            left_cx = sum(x for x, y in left_iris) // len(left_iris)
            left_cy = sum(y for x, y in left_iris) // len(left_iris)
            right_cx = sum(x for x, y in right_iris) // len(right_iris)
            right_cy = sum(y for x, y in right_iris) // len(right_iris)

            # 홍채 중심점 표시
            cv2.circle(frame, (left_cx, left_cy), 3, (0, 255, 0), -1)  # 왼쪽 홍채 중심 (초록색)
            cv2.circle(frame, (right_cx, right_cy), 3, (0, 255, 0), -1)  # 오른쪽 홍채 중심 (초록색)

            # 홍채 좌표 출력
            print(f"왼쪽 눈 홍채: ({left_cx}, {left_cy}), 오른쪽 눈 홍채: ({right_cx}, {right_cy})")

    cv2.imshow("Face & Iris Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()