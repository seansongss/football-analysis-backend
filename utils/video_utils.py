import cv2

# read_video(string) : List[frame]
# reads a video file and returns a list of frames
def read_video(video_path):
    cap =  cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames

# save_video(List[frame], string) : None
# saves a list of frames to a video file
def save_video(output_video_frames, output_video_path):
    # video format
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # out = cv2.VideoWriter(video_path, output_video, fps, (height, width))
    out = cv2.VideoWriter(output_video_path, fourcc, 24, (output_video_frames[0].shape[1], output_video_frames[0].shape[0]))
    
    # look over the frames and write them to the video writer
    for frame in output_video_frames:
        out.write(frame)
    out.release()

