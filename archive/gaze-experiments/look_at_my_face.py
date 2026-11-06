import cv2
import mediapipe as mp

# Mediapipe Face Mesh 초기화
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()
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

    # 결과에서 랜드마크 그리기
    if result.multi_face_landmarks:
        for landmarks in result.multi_face_landmarks:
            drawing_utils.draw_landmarks(
                frame, landmarks, mp_face_mesh.FACEMESH_TESSELATION
            )

    # 화면에 표시
    cv2.imshow("Face Mesh", frame)

    # 'q'를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()