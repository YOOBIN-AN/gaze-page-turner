import cv2
import mediapipe as mp
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates as denormalize_coordinates

cap = cv2.VideoCapture(0)

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

LEFT_IRIS = 468
RIGHT_IRIS = 473

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
                    return (pt[0] - center_x, pt[1] - center_y)

                rel_left = relative_coords(left_eye)
                rel_right = relative_coords(right_eye)

                cv2.putText(cropped, f"Left Eye: ({rel_left[0]}, {rel_left[1]})", (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(cropped, f"Right Eye: ({rel_right[0]}, {rel_right[1]})", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

                # 원본 프레임에 face mesh 그리기
                mp_drawing.draw_landmarks(
                    display_frame,
                    results.multi_face_landmarks[0],
                    mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=1, circle_radius=1),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)
                )

                # 두 개 화면 띄우기: 원본 (mesh 표시), 크롭 (좌표 표시)
                cv2.imshow("Full Frame with Mesh", display_frame)
                cv2.imshow("Zoomed Eye Region", cropped)
            else:
                cv2.imshow("Full Frame with Mesh", display_frame)
        else:
            cv2.imshow("Full Frame with Mesh", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()