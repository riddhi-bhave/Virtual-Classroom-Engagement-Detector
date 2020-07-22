import cv2
def video_setup(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    return fps

print(video_setup('zoom_practice/zoom_0.mp4'))