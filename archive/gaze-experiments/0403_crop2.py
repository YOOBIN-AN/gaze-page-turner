import cv2
import mediapipe as mp
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates as denormalize_coordinates

# 웹캠 열기
cap = cv2.VideoCapture(0)

# MediaPipe 설정
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# 눈동자 랜드마크 인덱스
LEFT_IRIS = 468
RIGHT_IRIS = 473

# 좌표 스케일 (움직임 확대해서 보이게)
SCALE = 5

# 격자 + 중심선 그리기 함수
def draw_grid(image):
    h, w = image.shape[:2]
    cx, cy = w // 2, h // 2
    step = 20
    for x in range(0, w, step):
        cv2.line(image, (x, 0), (x, h), (100, 100, 100), 1)
    for y in range(0, h, step):
        cv2.line(image, (0, y), (w, y), (100, 100, 100), 1)
    cv2.line(image, (cx, 0), (cx, h), (0, 0, 255), 1)
    cv2.line(image, (0, cy), (w, cy), (0, 0, 255), 1)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("카메라에서 프레임을 읽을 수 없습니다.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        ih, iw, _ = frame.shape
        display_frame = frame.copy()

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark

            left_eye = denormalize_coordinates(landmarks[LEFT_IRIS].x, landmarks[LEFT_IRIS].y, iw, ih)
            right_eye = denormalize_coordinates(landmarks[RIGHT_IRIS].x, landmarks[RIGHT_IRIS].y, iw, ih)

            if left_eye and right_eye:
                center_x = (left_eye[0] + right_eye[0]) // 2
                center_y = (left_eye[1] + right_eye[1]) // 2

                margin = 80
                x1 = max(min(left_eye[0], right_eye[0]) - margin, 0)
                y1 = max(min(left_eye[1], right_eye[1]) - margin, 0)
                x2 = min(max(left_eye[0], right_eye[0]) + margin, iw)
                y2 = min(max(left_eye[1], right_eye[1]) + margin, ih)

                cropped = frame[y1:y2, x1:x2].copy()

                def relative_coords(pt):
                    return ((pt[0] - center_x) * SCALE, (pt[1] - center_y) * SCALE)

                rel_left = relative_coords(left_eye)
                rel_right = relative_coords(right_eye)

                # 모눈종이 + 중심선
                draw_grid(cropped)

                # 좌표 텍스트
                cv2.putText(cropped, f"Left Eye: ({int(rel_left[0])}, {int(rel_left[1])})", (10, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(cropped, f"Right Eye: ({int(rel_right[0])}, {int(rel_right[1])})", (10, 55),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                # 원본 프레임에 전체 Face Mesh 표시
                mp_drawing.draw_landmarks(
                    display_frame,
                    results.multi_face_landmarks[0],
                    mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=1, circle_radius=1),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)
                )

                # 화면 표시
                cv2.imshow("Full Frame with Mesh", display_frame)
                cv2.imshow("Zoomed Eye Region", cropped)
            else:
                cv2.imshow("Full Frame with Mesh", display_frame)
        else:
            cv2.imshow("Full Frame with Mesh", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC 키 종료
            break

finally:
    cap.release()
    cv2.destroyAllWindows()