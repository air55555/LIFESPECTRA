import cv2
import numpy as np

def generate_osd_frame(frame):
    # Copy the original frame to prevent modification of the original image
    osd_frame = frame.copy()

    # Add text to the OSD frame
    text = "Recording"  # Example text
    text_position = (20, 40)  # Position of the text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (255, 255, 255)  # White color
    thickness = 2
    cv2.putText(osd_frame, text, text_position, font, font_scale, color, thickness)

    # Add a rectangle border to the OSD frame
    border_color = (0, 0, 255)  # Red color
    border_thickness = 2
    cv2.rectangle(osd_frame, (50, 50), (frame.shape[1]-10, frame.shape[0]-20), border_color, border_thickness)

    return osd_frame

# Capture frame from camera (replace with actual camera capture)
frame = np.zeros((480, 640, 3), dtype=np.uint8)
frame.fill(128)  # Fill frame with gray color

# Generate OSD frame
osd_frame = generate_osd_frame(frame)

# Display the OSD frame
cv2.imwrite("osd_frame.jpg", osd_frame)
#cv2.imshow("OSD Frame", osd_frame)
#cv2.waitKey(0)
#cv2.destroyAllWindows()