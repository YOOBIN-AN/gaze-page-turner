import cv2
import mediapipe as mp
import time
import wave
import numpy as np
import os
import pygame
from threading import Thread
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates as denormalize_coordinates

# 기본 설정
LEFT_IRIS = 468
RIGHT_IRIS = 473
SCALE = 20
GAZE_THRESHOLD = 30
GAUGE_MAX = 100
GAUGE_STEP = 2

LEFT_SOUND = "left_sound.wav"
RIGHT_SOUND = "right_sound.wav"

# 사운드 초기화
pygame.mixer.init()

def generate_beep(filename, freq=440):
    framerate = 44100
    duration = 0.2
    t = np.linspace(0, duration, int(framerate * duration), endpoint=False)
    waveform = (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)

    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(framerate)
        f.writeframes(waveform.tobytes())

# 소리 파일 없으면 자동 생성
for sound_file, freq in [(LEFT_SOUND, 440), (RIGHT_SOUND, 660)]:
    if not os.path.exists(sound_file):
        generate_beep(sound_file, freq)

def play_sound_async(path):
    def play():
        pygame.mixer.Sound(path).play()
    Thread(target=play, daemon=True).start()

def draw_gaze_zones(image):
    h, w = image.shape[:2]
    cx, cy = w // 2, h // 2
    overlay = image.copy()
    alpha = 0.2
    zone_color = (0, 255, 255)

    cv2.rectangle(overlay, (0, cy), (cx, h), zone_color, -1)
    cv2.putText(overlay, "LEFT TRIGGER ZONE", (10, h - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 255), 2)
    cv2.rectangle(overlay, (cx, cy), (w, h), zone_color, -1)
    cv2.putText(overlay, "RIGHT TRIGGER ZONE", (cx + 10, h - 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 100), 2)

    return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

def draw_gauge(image, value, position, color):
    x, y = position
    width = 100
    height = 15
    filled = int(width * (value / GAUGE_MAX))
    cv2.rectangle(image, (x, y), (x + width, y + height), (180, 180, 180), 1)
    cv2.rectangle(image, (x, y), (x + filled, y + height), color, -1)

# 메인 루프
cap = cv2.VideoCapture(0)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

left_gauge = 0
right_gauge = 0
left_triggered = False
right_triggered = False

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        ih, iw, _ = frame.shape
        frame = cv2.resize(frame, (int(iw * 1.2), int(ih * 1.2)))  # 전체 화면 확대

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        ih, iw, _ = frame.shape

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            left_eye = denormalize_coordinates(landmarks[LEFT_IRIS].x, landmarks[LEFT_IRIS].y, iw, ih)
            right_eye = denormalize_coordinates(landmarks[RIGHT_IRIS].x, landmarks[RIGHT_IRIS].y, iw, ih)

            if left_eye and right_eye:
                center_x = (left_eye[0] + right_eye[0]) // 2
                center_y = (left_eye[1] + right_eye[1]) // 2

                def relative_coords(pt):
                    return ((pt[0] - center_x) * SCALE, (pt[1] - center_y) * SCALE)

                rel_left = relative_coords(left_eye)
                gaze_x, gaze_y = rel_left

                # 눈 위치 표시
                cv2.circle(frame, left_eye, 5, (0, 255, 0), -1)
                cv2.circle(frame, right_eye, 5, (255, 0, 0), -1)

                # 좌표 표시
                cv2.putText(frame, f"Left Eye: ({int(gaze_x)}, {int(gaze_y)})", (30, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # 응시 감지 → 게이지
                if gaze_x < -GAZE_THRESHOLD and gaze_y > GAZE_THRESHOLD:
                    left_gauge = min(left_gauge + GAUGE_STEP, GAUGE_MAX)
                else:
                    left_gauge = max(left_gauge - GAUGE_STEP * 2, 0)

                if gaze_x > GAZE_THRESHOLD and gaze_y > GAZE_THRESHOLD:
                    right_gauge = min(right_gauge + GAUGE_STEP, GAUGE_MAX)
                else:
                    right_gauge = max(right_gauge - GAUGE_STEP * 2, 0)

                # 소리 반응
                if left_gauge >= GAUGE_MAX and not left_triggered:
                    play_sound_async(LEFT_SOUND)
                    left_triggered = True
                elif left_gauge == 0:
                    left_triggered = False

                if right_gauge >= GAUGE_MAX and not right_triggered:
                    play_sound_async(RIGHT_SOUND)
                    right_triggered = True
                elif right_gauge == 0:
                    right_triggered = False

                # 게이지 표시
                draw_gauge(frame, left_gauge, (10, frame.shape[0] - 30), (0, 255, 0))
                draw_gauge(frame, right_gauge, (frame.shape[1] - 110, frame.shape[0] - 30), (255, 0, 0))

                # 응시 영역 시각화
                frame = draw_gaze_zones(frame)

        cv2.imshow("Eye Tracking Full View", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()