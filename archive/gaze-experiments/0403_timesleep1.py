import cv2
import mediapipe as mp
import time
from playsound import playsound
from threading import Thread
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates as denormalize_coordinates

cap = cv2.VideoCapture(0)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

LEFT_IRIS = 468
RIGHT_IRIS = 473

SCALE = 20
GRID_STEP = 25
GAZE_THRESHOLD = 30      # 더 쉽게 감지되도록
GAZE_HOLD_TIME = 1.0     # 1초만 응시해도 OK

left_start = None
right_start = None

def play_sound_async(path):
    Thread(target=playsound, args=(path,), daemon=True).start()

def draw_grid(image):
    h, w = image.shape[:2]
    cx, cy = w // 2, h // 2
    font = cv2.FONT_HERSHEY_PLAIN

    for x in range(0, w, GRID_STEP):
        cv2.line(image, (x, 0), (x, h), (100, 100, 100), 1)
        rel_x = (x - cx) * SCALE
        if abs(rel_x) % (GRID_STEP * SCALE) == 0:
            label = f"{int(rel_x)}"
            cv2.putText(image, label, (x + 2, cy + 12), font, 1, (150, 150, 150), 1)

    for y in range(0, h, GRID_STEP):
        cv2.line(image, (0, y), (w, y), (100, 100, 100), 1)
        rel_y = (y - cy) * SCALE
        if abs(rel_y) % (GRID_STEP * SCALE) == 0:
            label = f"{-int(rel_y)}"
            cv2.putText(image, label, (cx + 4, y - 4), font, 1, (150, 150, 150), 1)

    cv2.line(image, (cx, 0), (cx, h), (0, 0, 255), 1)
    cv2.line(image, (0, cy), (w, cy), (0, 0, 255), 1)
    cv2.putText(image, "(0, 0)", (cx + 5, cy - 5), font, 1.2, (0, 0, 255), 2)

def draw_gaze_zones(image):
    h, w = image.shape[:2]
    cx, cy = w // 2, h // 2
    overlay = image.copy()
    alpha = 0.2
    zone_color = (0, 255, 255)

    # 왼쪽 아래
    cv2.rectangle(overlay, (0, cy), (cx, h), zone_color, -1)
    # 오른쪽 아래
    cv2.rectangle(overlay, (cx, cy), (w, h), zone_color, -1)

    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

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
        now = time.time()

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
                gaze_x, gaze_y = rel_left

                draw_grid(cropped)
                cropped = draw_gaze_zones(cropped)

                cv2.putText(cropped, f"Left Eye: ({int(gaze_x)}, {int(gaze_y)})", (10, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # 왼쪽 아래 응시
                if gaze_x < -GAZE_THRESHOLD and gaze_y > GAZE_THRESHOLD:
                    if not left_start:
                        left_start = now
                    elif now - left_start > GAZE_HOLD_TIME:
                        print("왼쪽 아래 응시 감지됨!")
                        play_sound_async("left_sound.mp3")
                        left_start = None
                else:
                    left_start = None

                # 오른쪽 아래 응시
                if gaze_x > GAZE_THRESHOLD and gaze_y > GAZE_THRESHOLD:
                    if not right_start:
                        right_start = now
                    elif now - right_start > GAZE_HOLD_TIME:
                        print("오른쪽 아래 응시 감지됨!")
                        play_sound_async("right_sound.mp3")
                        right_start = None
                else:
                    right_start = None

                cv2.imshow("Zoomed Eye Region", cropped)
            else:
                cv2.imshow("Zoomed Eye Region", frame)
        else:
            cv2.imshow("Zoomed Eye Region", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()