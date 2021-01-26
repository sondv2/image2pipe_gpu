import cv2

def get_frame_rate(video_url):
    cam = cv2.VideoCapture(video_url)
    fps = cam.get(cv2.CAP_PROP_FPS)
    return fps