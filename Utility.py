import cv2
import mediapipe as mp
import numpy as np

cap = cv2.VideoCapture(0)

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions( base_options=BaseOptions(model_asset_path='models/face_landmarker.task'), running_mode=VisionRunningMode.IMAGE)
 
landmarker = FaceLandmarker.create_from_options(options)

smoothed_z = 0
alpha = 0.1


def draw_room(frame, head_x, head_y, depth):
    h, w, _ = frame.shape

    front = [(0, 0),(w, 0),(w, h),(0, h)]

    min_scale = 0.6  
    max_scale = 0.9  
    inner_scale = min_scale + depth * (max_scale - min_scale)
    inner_w = int(w * inner_scale)
    inner_h = int(h * inner_scale)

    offset_x = (w - inner_w) // 2
    offset_y = (h - inner_h) // 2

    shift_x = int(head_x * w * 0.3)
    shift_y = int(head_y * h * 0.3)

    back = [(offset_x + shift_x, offset_y + shift_y),(offset_x + inner_w + shift_x, offset_y + shift_y),(offset_x + inner_w + shift_x, offset_y + inner_h + shift_y),(offset_x + shift_x, offset_y + inner_h + shift_y)]

    for i in range(4):
        cv2.line(frame, front[i], back[i], (0, 255, 0), 2)

    for i in range(4):
        cv2.line(frame, back[i], back[(i+1) % 4], (0, 255, 0), 2)

def main():
    global smoothed_z
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        result = landmarker.detect(mp_image)

        if result.face_landmarks:
            face = result.face_landmarks[0]
            nose = face[1]
            head_x = nose.x - 0.5
            head_y = nose.y - 0.5
            depth_indices = [1, 33, 263, 168]
            total_z = 0

            for idx in depth_indices:
                total_z += face[idx].z

            avg_z = total_z / len(depth_indices)

            smoothed_z = (1 - alpha) * smoothed_z + alpha * avg_z

            min_z = -0.04
            max_z = 0.00

            depth = (smoothed_z - max_z) / (min_z - max_z)
            depth = max(0, min(1, depth))

            draw_room(frame, head_x, head_y, 0.2)

            text = f"X:{head_x:.2f} Y:{head_y:.2f} Z:{depth:.2f}"
            cv2.putText(frame, text, (20, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.6,(0, 255, 0), 2)

        cv2.imshow('Head Tracked Room', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break

    landmarker.close()
    cap.release()
    cv2.destroyAllWindows()


def getHeadCoor():
    global smoothed_z
    ret, frame = cap.read()
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    head_x = 0
    head_y = 0
    result = landmarker.detect(mp_image)

    if result.face_landmarks:
        face = result.face_landmarks[0]
        nose = face[1]
        head_x = nose.x - 0.5
        head_y = nose.y - 0.5
        depth_indices = [1, 33, 263, 168]
        total_z = 0

        for idx in depth_indices:
            total_z += face[idx].z

        avg_z = total_z / len(depth_indices)

        smoothed_z = (1 - alpha) * smoothed_z + alpha * avg_z

        min_z = -0.04
        max_z = 0.00

        depth = (smoothed_z - max_z) / (min_z - max_z)
        depth = max(0, min(1, depth))
    return head_x,head_y

if __name__ == "__main__":
    main()