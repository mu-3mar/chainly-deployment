import cv2

url = "rtsp://20.51.117.96:8554/live/live?rtsp_transport=udp"

cap = cv2.VideoCapture(url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    cv2.imshow("Stream", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()