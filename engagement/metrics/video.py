import cv2

## determines frames per second
def video_setup(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps

## finds frames based on noise present
def video_frames(noise, pps, fps, time):
    frames = []
    for point in noise:
        ptf = point // (pps / fps)
        if ptf not in frames:
            frames += [float(ptf)]
    return frames

## calculates video metrics
def video_metrics(frames, fps, time):
  video_sec = len(frames) / fps
  video_pct = video_sec / time[len(time) - 1]
  return video_sec, video_pct

## runs video script
def video_run(path, noise, pps, time):
    fps = video_setup(path)
    frames = video_frames(noise, pps, fps, time)
    video_sec, video_pct = video_metrics(frames, fps, time)
    return frames, video_sec, video_pct