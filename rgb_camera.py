import cv2
import time
import numpy as np

"""
save frame every (duration) seconds , stand alone parallel process for normal functioning
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
                x, y, w, h = 100, 100, 400, 300

                frame = blur_outside_rectangle(frame, x, y, w, h)
                frame = generate_osd_frame(frame, x, y, w, h, "")


                # Save the frame as a JPEG file

                cv2.imwrite(file_name, frame)

                print(f"Photos captured and saved to '{file_name}'")
                print(time.time_ns())
                # Wait for 1 second before capturing the next photo
                time.sleep(duration)

            else:
                print("Error: Failed to capture frame")
                break

    finally:
        # Release the camera
        camera.release()

def generate_osd_frame(frame,x, y, w, h,text):
    # Define the coordinates of the rectangle region (x, y, width, height)

    # Copy the original frame to prevent modification of the original image
    osd_frame = frame.copy()

    # Add text to the OSD frame
    #text = "Recording"  # Example text
    text_position = (50, 50)  # Position of the text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (255, 255, 255)  # White color
    thickness = 2
    cv2.putText(osd_frame, text, text_position, font, font_scale, color, thickness)

    # Add a rectangle border to the OSD frame
    border_color = (0, 0, 255)  # Red color
    border_thickness = 2
    cv2.rectangle(osd_frame, (x, y), (x+w, y+h), border_color, border_thickness)

    return osd_frame

def blur_outside_rectangle(frame, x, y, w, h):
    # Create a mask with the same size as the frame
    mask = np.zeros_like(frame, dtype=np.uint8)

    # Define the rectangle region in the mask
    cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)

    # Apply blur effect to the area outside the rectangle
    blurred_frame = cv2.blur(frame, (21, 21))

    # Apply the mask to blur only outside the rectangle
    result = cv2.bitwise_and(frame, mask)
    result += cv2.bitwise_and(blurred_frame, cv2.bitwise_not(mask))

    return result


if __name__ == "__main__":
    file_name = "app/static/image.jpg"  # Output file name
    duration = 0.5  # Duration in seconds

    capture_and_save_photos(file_name, duration)
