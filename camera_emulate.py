import cv2

# Replace with the path to your video file
video_path = "test_data/file_example.AVI.avi"

cap = cv2.VideoCapture(video_path)

# Get frame size from the video capture object
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Use DirectShow for video writing (might be more reliable)
writer = cv2.VideoWriter(0, cv2.VideoWriter_fourcc(*'XVID'),
                         cap.get(cv2.CAP_PROP_FPS), (frame_width, frame_height))

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to capture frame")
        break

    writer.write(frame)

    # Process the frame here (e.g., display)
    # cv2.imshow('Camera', frame)  # Optional for debugging

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
writer.release()
cv2.destroyAllWindows()
