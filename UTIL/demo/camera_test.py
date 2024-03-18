import cv2
import time




# RTSP 주소
rtsp_url = "rtsp://192.168.0.178/avc"
# ax8 기준 8이 최대
try:
    cap = cv2.VideoCapture(rtsp_url)
    cap.set(cv2.CAP_PROP_FPS, 7)
except:
    print("not connect")

# RTSP 스트림이 열렸는지 확인
if not cap.isOpened():
    print("Error: Couldn't open the RTSP stream.")
    exit()

cnt = 0
fps = 0
frame_count = 0
start_time = time.time()
while True:
    # 현재 시간 측정
    current_time = time.time()

    # 한 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        break

    cnt += 1
    cv2.imshow("image", frame)
    cv2.waitKey(1)
    # cv2.imwrite(f"./save/{cnt}.jpg", frame)
    
    # 프레임 카운트 증가
    frame_count += 1
    
    # 경과 시간 계산
    elapsed_time = current_time - start_time
    
    # 매 초마다 FPS 계산
    if elapsed_time > 1.:
        fps = frame_count / elapsed_time
        print(f"FPS: {fps:.2f}")
        frame_count = 0
        start_time = current_time
    time.sleep(0.01)

# VideoCapture 객체 해제
cap.release()
