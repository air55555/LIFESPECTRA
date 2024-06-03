"""
Backend server for LIFESPECTRA
"""
from fastapi import FastAPI, Request, HTTPException, Query, File
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import pathlib
from datetime import datetime
import logging
from colorlog import ColoredFormatter
import cv2
import uvicorn
import os
import base64
from utils import *
from collections import deque
import time

WP_PORT = "10004"
WP_CAMERA_PAGE = "Camera1"
cwd = pathlib.Path(__file__).parent.resolve()
EMUL = True  # Set to True if emulating moving hardware

app = FastAPI()
rate_limit_window = 500  # milliseconds
last_request_time = 0

# Setup Logging Configuration
log_format = '\033[34m%(asctime)s\033[0m - %(log_color)s%(levelname)s%(reset)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'
color_formatter = ColoredFormatter(
    log_format,
    date_format,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)

log_handler = logging.StreamHandler()
log_handler.setFormatter(color_formatter)
root_logger = logging.getLogger()
root_logger.addHandler(log_handler)
root_logger.setLevel(logging.INFO)

# Create FastAPI logging Middleware
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
            execution_time = (end_time - start_time).total_seconds()
            logging.info(f"{scope['method']} {scope['path']} - Completed in {execution_time} seconds")
        else:
            await self.app(scope, receive, send)

# Add Logging Middleware
app.add_middleware(LoggingMiddleware)
print(f'IP address of backend server {get_ip()}')
# Rate Limiting Middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    global last_request_time
    current_time = time.time() * 1000  # convert to milliseconds
    if request.url.components.path=="/iiimage_small":
        if current_time - last_request_time < rate_limit_window:
            #pass
            logging.warning("Rate limit exceeded. Please try again later.")
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Please try again later."})
    last_request_time = current_time
    response = await call_next(request)
    return response
# async def rate_limiting_middleware(request: Request, call_next):
#     global last_request_time
#     current_time = time.time() * 1000  # convert to milliseconds
#     if current_time - last_request_time < rate_limit_window:
#         raise HTTPException(status_code=429, detail="Too many requests, please try again later.")
#     last_request_time = current_time
#     response = await call_next(request)
#     return response

# Emulated Camera Controller
if EMUL:
    emul_camera_controller = CameraController()

@app.get("/delete_requests")
async def clear_requests():
    global requests
    requests = []
    return {"message": "All requests cleared successfully"}

@app.get("/slow_left")
async def slow_left():
    return ""

@app.get("/camera_home")
async def camera_home():
    real_cam_move_home()
    return RedirectResponse(f"http://localhost:{WP_PORT}/{WP_CAMERA_PAGE}/")

@app.get("/camera_up")
async def camera_up(param: str = Query(None)):
    if EMUL:
        emul_camera_controller.move_up()
    else:
        real_cam_move_up()
    if param is not None:
        return {"message": "OK"}
    else:
        return RedirectResponse(f"http://localhost:{WP_PORT}/{WP_CAMERA_PAGE}/")

@app.get("/camera_down")
async def camera_down(param: str = Query(None)):
    if EMUL:
        emul_camera_controller.move_down()
    else:
        real_cam_move_down()
    if param is not None:
        return {"message": "OK"}
    else:
        return RedirectResponse(f"http://localhost:{WP_PORT}/{WP_CAMERA_PAGE}/")

@app.get("/camera_left")
async def camera_left(param: str = Query(None)):
    if EMUL:
        emul_camera_controller.move_left()
    else:
        real_cam_move_left()
    if param is not None:
        return {"message": "OK"}
    else:
        return RedirectResponse(f"http://localhost:{WP_PORT}/{WP_CAMERA_PAGE}/")

@app.get("/camera_right")
async def camera_right(param: str = Query(None)):
    if EMUL:
        emul_camera_controller.move_right()
    else:
        real_cam_move_right()
    if param is not None:
        return {"message": "OK"}
    else:
        return  RedirectResponse(f"http://localhost:{WP_PORT}/{WP_CAMERA_PAGE}/")


@app.get("/dummy")
async def dummy():
    pass

@app.get("/")
async def read_root():
    return {"message": "Lifespectra app backend"}

@app.get('/health')
async def health_check():
    return "Server OK", 200

@app.get("/image_small")
async def get_image():
    image_path = "app/static/image.jpg"
    if os.path.exists(image_path):
        # Read the image
        image = cv2.imread(image_path)

        # Resize the image to 320x240
        resized_image = cv2.resize(image, (320, 240))
        resized_image = generate_osd_frame(resized_image, 100, 100, 100, 100, "small")
        # Encode the resized image as base64
        _, encoded_image = cv2.imencode('.jpg', resized_image)
        cv2.imwrite("app/static/image_small.jpg", resized_image,[cv2.IMWRITE_JPEG_QUALITY, 1])
    return FileResponse("app/static/image_small.jpg")
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

@app.get("/image64")
async def get_image():
    """
    base64 encoded string
    """
    image_path = "app/static/image.jpg"
    if os.path.exists(image_path):
        # Read the image
        image = cv2.imread(image_path)

        # Resize the image to 320x240
        resized_image = cv2.resize(image, (320, 240))
        resized_image = generate_osd_frame(resized_image, 100, 100, 100, 100, "small")
        # Encode the resized image as base64
        _, encoded_image = cv2.imencode('.jpg', resized_image)
        image_base64 = base64.b64encode(encoded_image).decode("utf-8")

        # Return the base64 image as JSON
        return JSONResponse(content={"image_base64": image_base64})
    else:
        return JSONResponse(content={"error": "Image not found"}, status_code=404)

if __name__ == '__main__':

    uvicorn.run(app, port=80, host='0.0.0.0', log_config=f"log.ini")


