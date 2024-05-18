import numpy as np
import cv2
import socket

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
# Function to move the camera to the left
MOVE_DISTANCE = 20  # Number of pixels to move
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480
"""
Emulator class
"""
class CameraController:
    def __init__(self):
        self.current_position = (1550, 1550)
        self.large_image = cv2.imread("test_data/big_txt.png")

    # Function to move the camera to the left
    def move_left(self):
        new_position = (self.current_position[0] - MOVE_DISTANCE, self.current_position[1])
        if (new_position[0] > 3200 or new_position[1] > 3200): new_position = (1550, 1550)
        new_image = self.large_image[self.current_position[1]:self.current_position[1] + IMAGE_HEIGHT, new_position[0]:new_position[0] + IMAGE_WIDTH]
        self.current_position = new_position
        self.save_image(new_image, "app/static/image.jpg")
        return new_image

    # Function to move the camera to the right
    def move_right(self):
        new_position = (self.current_position[0] + MOVE_DISTANCE, self.current_position[1])
        if (new_position[0] > 4600 or new_position[1] > 3200 or new_position[0]<0 or new_position[1]<0): new_position = (1550, 1550)
        new_image = self.large_image[self.current_position[1]:self.current_position[1] + IMAGE_HEIGHT, new_position[0]:new_position[0] + IMAGE_WIDTH]
        self.current_position = new_position
        self.save_image(new_image, "app/static/image.jpg")
        return new_image

    # Function to move the camera up
    def move_up(self):
        new_position = (self.current_position[0], self.current_position[1] - MOVE_DISTANCE)
        if (new_position[0] > 4600 or new_position[1] > 3200 or new_position[0]<0 or new_position[1]<0): new_position = (1550, 1550)
        print(new_position)
        new_image = self.large_image[new_position[1]:new_position[1] + IMAGE_HEIGHT, self.current_position[0]:self.current_position[0] + IMAGE_WIDTH]
        self.current_position = new_position
        self.save_image(new_image, "app/static/image.jpg")
        return new_image

    # Function to move the camera down
    def move_down(self):
        new_position = (self.current_position[0], self.current_position[1] + MOVE_DISTANCE)
        if (new_position[0] > 4600 or new_position[1] > 3200 or new_position[0]<0 or new_position[1]<0): new_position = (1550, 1550)
        new_image = self.large_image[self.current_position[1]:self.current_position[1] + IMAGE_HEIGHT, new_position[0]:new_position[0] + IMAGE_WIDTH]
        self.current_position = new_position
        self.save_image(new_image, "app/static/image.jpg")
        return new_image


    # Function to save an image to a file
    def save_image(self, image, file_path):
        x, y, w, h = 100, 100, 400, 300
        image = blur_outside_rectangle(image, x, y, w, h)
        image = generate_osd_frame(image, x, y, w, h, "")
        cv2.imwrite(file_path, image)
        print(self.current_position)

def real_cam_move_up():
    pass

def real_cam_move_down():
    pass

def real_cam_move_left():
    pass

def real_cam_move_right():
    pass

def real_cam_move_home():
    pass

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
