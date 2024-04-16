# import time
import PySimpleGUI as sg
import hspec_camera
import scanner
from math import tan, radians
import numpy as np
import cv2
from collections import deque
from harvesters.core import Harvester
import harvesters
from spectral import *
import os
from matplotlib.ticker import NullFormatter
# import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import shutil
#import visca_rgb
import lidar
from statistics import mean
import warnings

warnings.simplefilter("ignore", ResourceWarning)
matplotlib.use('TkAgg')


def create_gen(expos: int, frames: int, name: str, specim, FPS):
    return specim.capturing(expos, frames, name, FPS) if frames else specim.calibration(expos, FPS)
def create_predefined_frame(width, height, text="sample", color=(255, 255, 255), font_scale=1.0, thickness=2):
  """
  Creates a predefined frame with text on it.

  Args:
      width: Width of the frame in pixels.
      height: Height of the frame in pixels.
      text: Text to display on the frame (default: "sample").
      color: Color of the text (default: white (255, 255, 255)).
      font_scale: Font size scaling factor (default: 1.0).
      thickness: Thickness of the text in pixels (default: 2).

  Returns:
      A NumPy array representing the predefined frame with text.
  """

  # Create a black (BGR) frame of the specified size.
  frame = np.zeros((height, width, 3), dtype=np.uint8)
  frame.fill(0)  # Fill with black color

  # Get text size using the specified font.
  text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)

  # Calculate text placement coordinates.
  text_x = int((width - text_size[0]) / 2)
  text_y = int((height + text_size[1]) / 2)

  # Add the text to the frame.
  cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

  return frame


def App():

    BTN_COLOR = ('white', '#0D7377')
    BGRND_COLOR = '#4D3E3E'
    MINI_FONT = 'Helvetica 10 bold italic'
    BIG_FONT = 'Helvetica 12 bold italic'
    capture_state_flag = 0
    videostream_windows = [
        [sg.Image(size=(1024, 100), k='-WATERFALL'),
         sg.VerticalSeparator(), sg.Image(size=(600, 100), k='-SONY')]
    ]
    videostream = [
        [sg.Frame('', videostream_windows, font=BIG_FONT, title_location=sg.TITLE_LOCATION_TOP)],
    ]
    layout = [
        [sg.Frame('VideoStream', videostream, font=BIG_FONT, title_location=sg.TITLE_LOCATION_TOP)]
    ]
    sg.theme('DarkBlack')
    window = sg.Window('Hyperspectral quality control system', layout, resizable=True, finalize=True,
                       text_justification='right', auto_size_text=False, default_element_size=(21, 1),
                       font=MINI_FONT, button_color=BTN_COLOR, element_justification='c')
    window.Maximize()

    cap = cv2.VideoCapture(0)

    while True:
        if capture_state_flag == 0:
            ret, frame = cap.read()
            if frame is None:
                width = 640
                height = 480
                text = "Sample"
                frame = create_predefined_frame(width, height, text)

            cv2.circle(frame, (640, 360), 5, (0, 255, 0), -1)
            window['-SONY'].update(data=cv2.imencode('.png', frame)[1].tobytes())

        try:
            event, values = window.read(timeout=0, timeout_key='timeout')
            if event == sg.WIN_CLOSED:
                try:
                    window.close()
                    specim.close_camera()
                    break
                except:
                    break

            ###########################################################################################################
            ############################## PLATFORM PTR-404 HM  #######################################################
            ###########################################################################################################

            elif event == '-RIGHT-RIGHT_MOVE':
                ptr.move_right('32')
            elif event == '-RIGHT':
                ptr.stop()
            elif event == '-LEFT-LEFT_MOVE':
                ptr.move_left()
            elif event == '-LEFT':
                ptr.stop()
            elif event == '-UP-UP_MOVE':
                ptr.move_up()
            elif event == '-UP':
                ptr.stop()
            elif event == '-DOWN-DOWN_MOVE':
                ptr.move_down()
            elif event == '-DOWN':
                ptr.stop()


            ###########################################################################################################
            ############################## Lidar Ouster OS1 - 128U ####################################################
            ###########################################################################################################

            elif event == '-GET_PLY':
               print("Get ply")

            ###########################################################################################################
            ############################## RGB Camera Sony FCB  #######################################################
            ###########################################################################################################


            ###########################################################################################################
            ############################## Capture HS camera  #########################################################
            ###########################################################################################################

            elif event == '-CAPTURE':
                capture_state_flag = 1
        except Exception as error:
            print(error)



if __name__ == '__main__':
    specim = hspec_camera.Camera()
    ptr = scanner.Ptr()
    App()