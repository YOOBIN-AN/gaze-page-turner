import cv2
import mediapipe as mp
import numpy as np

class HeadPoseGazeTracker:
    def __init__(self):
        """ 초기 설정: MediaPipe 모델 & OpenCV 카메라 초기화 """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)
        self.cap = cv2.VideoCapture(0)  # 노트북 웹캠 사용

        # 머리 3D 포즈 추정을 위한 주요 랜드마크 (MediaPipe FaceMesh 기준)
        self.FACE_LANDMARKS_IDXS = [33, 263, 1, 61, 291, 199]  # (왼쪽눈, 오른쪽눈, 코, 입 좌우, 턱 끝)
        
        # 3D 모델 좌표 설정 (정면 기준)
        self.model_3d_points = np.array([
            [-30, -30, 30],  # 왼쪽 눈 (33)
            [30, -30, 30],   # 오른쪽 눈 (263)
            [0, 0, 0],       # 코끝 (1)
            [-20, 20, 20],   # 왼쪽 입 (61)
            [20, 20, 20],    # 오른쪽 입 (291)
            [0, 30, 10]      # 턱 끝 (199)
        ], dtype=np.float64)

        # 카메라 내부 행렬 (기본값, 필요 시 조정)
        self.camera_matrix = np.array([
            [640, 0, 320],  # focal length x, skew, center x
            [0, 640, 240],  # skew, focal length y, center y
            [0, 0, 1]       # projection
        ], dtype=np.float64)

        self.dist_coeffs = np.zeros((4,1))  # 왜곡 계수 (없음)

    def get_frame(self):
        """ 프레임을 받아와 RGB 변환 후 얼굴 분석 """
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(rgb_frame)
        return frame, result

    def estimate_head_pose(self, frame, face_landmarks):
        """ 머리의 3D 포즈(회전 각도) 계산 """
        height, width, _ = frame.shape

        # 2D 랜드마크 좌표 추출
        image_points = np.array([
            [face_landmarks.landmark[idx].x * width, face_landmarks.landmark[idx].y * height]
            for idx in self.FACE_LANDMARKS_IDXS
        ], dtype=np.float64)

        # SolvePnP를 사용하여 3D-2D 변환
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_3d_points, image_points, self.camera_matrix, self.dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        if success:
            # 회전 벡터를 Euler 각도 (yaw, pitch, roll)로 변환
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rotation_matrix)
            yaw, pitch, roll = angles  # 머리 회전 각도

            return yaw, pitch, roll, rotation_vector, translation_vector
        return None, None, None, None, None

    def draw_head_pose(self, frame, rotation_vector, translation_vector):
        """ 머리 방향을 시각적으로 표시 """
        if rotation_vector is None or translation_vector is None:
            return

        # 3D 축을 표시할 기준점
        axis_length = 50
        axis_3d_points = np.array([
            [axis_length, 0, 0],   # X 축 (빨강)
            [0, axis_length, 0],   # Y 축 (초록)
            [0, 0, axis_length],   # Z 축 (파랑)
            [0, 0, 0]              # 원점 추가
        ], dtype=np.float64)

        # 3D -> 2D 변환
        axis_2d_points, _ = cv2.projectPoints(axis_3d_points, rotation_vector, translation_vector, self.camera_matrix, self.dist_coeffs)

        # 원점 (머리 중심)
        origin = tuple(axis_2d_points[3].ravel().astype(int))

        # X, Y, Z 축 표시
        cv2.line(frame, origin, tuple(axis_2d_points[0].ravel().astype(int)), (0, 0, 255), 2)  # X축 (빨강)
        cv2.line(frame, origin, tuple(axis_2d_points[1].ravel().astype(int)), (0, 255, 0), 2)  # Y축 (초록)
        cv2.line(frame, origin, tuple(axis_2d_points[2].ravel().astype(int)), (255, 0, 0), 2)  # Z축 (파랑)

    def run(self):
        """ 실시간 영상 분석 루프 """
        while self.cap.isOpened():
            frame, result = self.get_frame()
            if frame is None:
                print("프레임을 가져올 수 없습니다.")
                break

            if result.multi_face_landmarks:
                for face_landmarks in result.multi_face_landmarks:
                    yaw, pitch, roll, rotation_vector, translation_vector = self.estimate_head_pose(frame, face_landmarks)

                    if yaw is not None:
                        # 회전 각도 출력
                        print(f"Yaw: {yaw:.2f}, Pitch: {pitch:.2f}, Roll: {roll:.2f}")

                        # 머리 방향 시각적 표시
                        self.draw_head_pose(frame, rotation_vector, translation_vector)

            cv2.imshow("Head Pose & Gaze Tracking", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tracker = HeadPoseGazeTracker()
    tracker.run()