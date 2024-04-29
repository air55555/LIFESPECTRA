import cv2
import time

"""
save frame every (duration) seconds 
"""
def capture_and_save_photos(file_name, duration):
    # Initialize the camera
    camera = cv2.VideoCapture(0)

    start_time = time.time()

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = camera.read()

            if ret:
                # Save the frame as a JPEG file
                cv2.imwrite(file_name, frame)

                print(f"Photos captured and saved to '{file_name}'")
                # Wait for 1 second before capturing the next photo
                time.sleep(duration)

            else:
                print("Error: Failed to capture frame")
                break

    finally:
        # Release the camera
        camera.release()




if __name__ == "__main__":
    file_name = "app/static/image.jpg"  # Output file name
    duration = 0.5  # Duration in seconds

    capture_and_save_photos(file_name, duration)
