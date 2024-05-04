import pathlib
from datetime import datetime
import logging
from urllib import request
import time
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, Response, Query
import cv2
import uvicorn
from utils import *

WP_PORT="10004"
WP_CAMERA_PAGE = "Camera1"

#Set to true if emulate moving hardware. Using big.png as source, cropping it .
EMUL=True
#EMUL=False

cwd = pathlib.Path(__file__).parent.resolve()
# Setup Logging Configuration
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Create FastAPI Middleware
class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            start_time = datetime.now()

            async def send_wrapper(message):
                if message['type'] == 'http.response.start':
                    logging.info(f"{scope['method']} {scope['path']} - {message['status']}")
                await send(message)

            await self.app(scope, receive, send_wrapper)

            end_time = datetime.now()
            execution_time = end_time - start_time
            logging.info(f"{scope['method']} {scope['path']} - Completed in {execution_time.total_seconds()} seconds")
        else:
            await self.app(scope, receive, send)


app = FastAPI()
app.add_middleware(LoggingMiddleware)
if EMUL:
    emul_camera_controller = CameraController()


# Perform random movements and capture images
#num_movements = 5  # Number of random movements
#movements = [camera_controller.move_left, camera_controller.move_right, camera_controller.move_up,
#             camera_controller.move_down]




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

def grab_camera_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    return frame

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer

@app.get("/delete_requests")
async def clear_requests():
    global requests
    requests = []
    return {"message": "All requests cleared successfully"}

@app.get("/slow_left")
async def slow_left():
    return ""

@app.get("/camera_home")
async def camera_up():
    real_cam_move_home()
    return RedirectResponse(f"http://localhost:{WP_PORT}/{WP_CAMERA_PAGE}/")
@app.get("/camera_up")
async def camera_up(param: str = Query(None)):
    if EMUL:
        emul_camera_controller.move_up()
    else:
        real_cam_move_up()
    if param is not None:
        global requests
        requests = []
        time.sleep(1)
        return {"message": "OK"}

    else:
        return RedirectResponse(f"http://localhost:{WP_PORT}/{WP_CAMERA_PAGE}/")

@app.get("/camera_down")
async def camera_down():
    if EMUL: emul_camera_controller.move_down()
    else: real_cam_move_down()
    return RedirectResponse(f"http://localhost:{WP_PORT}/{WP_CAMERA_PAGE}/")

@app.get("/camera_left")
async def camera_left():
    if EMUL: emul_camera_controller.move_left()
    else: real_cam_move_left()
    return RedirectResponse(f"http://localhost:{WP_PORT}/{WP_CAMERA_PAGE}/")

@app.get("/camera_right")
async def camera_right():
    if EMUL: emul_camera_controller.move_right()
    else: real_cam_move_right()
    return RedirectResponse(f"http://localhost:{WP_PORT}/{WP_CAMERA_PAGE}/")

@app.get("/capture")
async def capture_image():
    # Define the coordinates of the rectangle region (x, y, width, height)

    x, y, w, h = 100, 100, 400, 300
    save_path = "app/static/image.jpg"
    frame = grab_camera_image()
    _, jpeg = cv2.imencode(".jpg", frame)
    #frame = generate_osd_frame(frame,x, y, w, h,"")
    frame=blur_outside_rectangle(frame, x, y, w, h)
    frame = generate_osd_frame(frame, x, y, w, h, "")
    cv2.imwrite(save_path, frame)

    # Return a response indicating the image path
    #return {"message": "Image captured successfully", "image_path": save_path}
    return RedirectResponse("http://localhost:10005/camera-move/")
    #return StreamingResponse(content=jpeg.tobytes(), media_type="image/jpeg")

@app.get("/")
async def read_root():
    return {"message": "Lifespectra app backend"}

@app.get('/health')
async def health_check():
    return "Server OK", 200

@app.get("/image")
async def get_image():
    return FileResponse("app/static/image.jpg")
@app.get("/logs")
async def read_last_logs():
    try:
        with open(f"{cwd}/logfile.log", "r") as file:
            lines = file.readlines()
            last_5_logs = lines[-20:]
            # Reverse the array using slicing
            last_5_logs = last_5_logs[::-1]
            return {"last_logs": last_5_logs}
    except FileNotFoundError:
        return {"error": "Log file not found."}


if __name__ == '__main__':

    uvicorn.run(app, port=80, host='0.0.0.0', log_config=f"log.ini")


