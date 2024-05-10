import pathlib
from datetime import datetime
import logging
from urllib import request
import time
from fastapi.responses import FileResponse
from fastapi.responses import RedirectResponse
from fastapi import  Query
import cv2
import uvicorn
from utils import *
import os
import base64
from fastapi import FastAPI, File
from fastapi.responses import JSONResponse

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
print(f'IP address  of backend server {get_ip()}')
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
        return RedirectResponse(f"http://localhost:{WP_PORT}/{WP_CAMERA_PAGE}/")

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

@app.get("/image64")
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
        image_base64 = base64.b64encode(encoded_image).decode("utf-8")

        # Return the base64 image as JSON
        return JSONResponse(content={"image_base64": image_base64})
    else:
        return JSONResponse(content={"error": "Image not found"}, status_code=404)

if __name__ == '__main__':

    uvicorn.run(app, port=80, host='0.0.0.0', log_config=f"log.ini")


