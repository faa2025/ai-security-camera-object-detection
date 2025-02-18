import cv2
import yt_dlp
url = "https://www.youtube.com/live/B1szF_KlLAI"
camera = cv2.VideoCapture(url)

def get_livestream_url(youtube_url):
    ydl_opts = {'quiet': True, 'format': 'best'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        return info_dict['url']  # Direct video stream URL

if not camera.isOpened():
    print("Cannot show stream")
    exit()
else:
    print("Showing stream...")
    while camera.isOpened():
        ret, frame = camera.read()
        if not ret:
            print("Cannot receive frame")
            break
        cv2.imshow('Camera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    camera.release()
    cv2.destroyAllWindows()
    print("Stream closed")
