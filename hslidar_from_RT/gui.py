import PySimpleGUI as sg
import hspec_camera
import scanner
#from math import tan, radians
import numpy as np
import cv2
from collections import deque
#from harvesters.core import Harvester
#import harvesters
#from spectral import *
#import os
#from matplotlib.ticker import NullFormatter
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
#import shutil
import lidar
#from statistics import mean
import warnings

warnings.simplefilter("ignore", ResourceWarning)
matplotlib.use('TkAgg')

def create_gen(expos: int, frames: int, name: str, specim, FPS, posit):
    return specim.capturing(expos, frames, name, FPS, posit) if frames else specim.calibration(expos, FPS)

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
    sg.theme('DarkBlack')

    main_path = 'C:\PyProj\HSLidar\Datasets'

    hsi_camera = [
        [sg.B('LIVE', size=(10, 1), enable_events=True, key='-LIVE'),
         sg.B('CAPTURE', size=(10, 1), enable_events=True, key='-CAPTURE')],
        [sg.B('STOP', size=(10, 1), enable_events=True, key='-STOP_LIVE')],
        [sg.T('Exposition, us'), sg.In('30000', size=(80, 1), k='-EXPOS_VALUE', background_color=BGRND_COLOR)],
        [sg.T('FPS'), sg.In('20', size=(80, 1), k='-FPS', background_color=BGRND_COLOR)],
        [sg.T('Data name'), sg.In(size=(30, 1), k='-DATA_NAME', background_color=BGRND_COLOR)],
    ]
    videostream_windows = [
        [sg.Image(size=(1024, 100), k='-WATERFALL'),
         sg.VerticalSeparator(), sg.Image(size=(600, 100), k='-SONY')]
    ]

    ptz_settings = [[sg.B(sg.SYMBOL_UP, size=(2, 1), enable_events=True, key='-UP')],
                    [sg.B('To start position', size=(12, 1), enable_events=True, key='-MOVE_TO_START_POSITION'),
                     sg.B(sg.SYMBOL_LEFT, size=(2, 1), enable_events=True, key='-LEFT'),
                     sg.B(sg.SYMBOL_RIGHT, enable_events=True, key='-RIGHT'),
                     sg.B('To end position', size=(12, 1), enable_events=True, key='-MOVE_TO_END_POSITION'), ],
                    [sg.B(sg.SYMBOL_DOWN, size=(2, 1), enable_events=True, key='-DOWN')],
                    [sg.B('Start position', size=(12, 1), enable_events=True, key='-SET_START'),
                     sg.T('Start position'),
                     sg.In('3f08', size=(20, 1), k='-START_POS_VALUE', background_color=BGRND_COLOR)],
                    [sg.B('End position', size=(12, 1), enable_events=True, key='-SET_END'),
                     sg.T('End position'),
                     sg.In('4c37', size=(20, 1), k='-END_POS_VALUE', background_color=BGRND_COLOR)],
                    ]

    rgb_camera = [[sg.T('')], [sg.T('ZOOM'),
                               sg.Slider(range=(1, 100), default_value=12, enable_events=True, orientation='horizontal',
                                         key='-ZOOM')], ]

    lidar_window = [[sg.B('Get ply', size=(10, 1), enable_events=True, key='-GET_PLY')], ]

    videostream = [
        [sg.Frame('', videostream_windows, font=BIG_FONT, title_location=sg.TITLE_LOCATION_TOP)],
        [sg.HorizontalSeparator()],
        [sg.Frame('HSI', hsi_camera, font=BIG_FONT, title_location=sg.TITLE_LOCATION_TOP, element_justification='c',
                  expand_x=True, expand_y=True), sg.VerticalSeparator(),
         sg.Frame('PTZ', ptz_settings, font=BIG_FONT, title_location=sg.TITLE_LOCATION_TOP, element_justification='c',
                  expand_x=True, expand_y=True), sg.VerticalSeparator(),
         sg.Frame('RGB', rgb_camera, font=BIG_FONT, title_location=sg.TITLE_LOCATION_TOP, element_justification='c',
                  expand_x=True, expand_y=True)],
        [sg.HorizontalSeparator()],
        [sg.Frame('Lidar', lidar_window, font=BIG_FONT, title_location=sg.TITLE_LOCATION_TOP, element_justification='c',
                  expand_x=True, expand_y=True)]
    ]

    layout = [
        [sg.Frame('VideoStream', videostream, font=BIG_FONT, title_location=sg.TITLE_LOCATION_TOP)]
    ]

    window = sg.Window('SHYL', layout, resizable=True, finalize=True,
                       text_justification='right', auto_size_text=False, default_element_size=(21, 1),
                       font=MINI_FONT, button_color=BTN_COLOR, element_justification='c')
    window.Maximize()

    window['-RIGHT'].bind("<ButtonPress-1>", '-RIGHT_MOVE')
    window['-RIGHT'].bind("<ButtonRelease-1>", '-RIGHT_STOP')


    window['-LEFT'].bind("<ButtonPress-1>", '-LEFT_MOVE')
    window['-LEFT'].bind("<ButtonRelease-1>", '-LEFT_STOP')

  #  window['-LEFT'].bind("<Left>", '-LEFT_MOVE')
    #window['-LEFT'].bind("<ButtonRelease-1>", '-LEFT_STOP')

    window['-UP'].bind("<ButtonPress-1>", '-UP_MOVE')
    window['-UP'].bind("<ButtonRelease-1>", '-UP_STOP')



    window['-DOWN'].bind("<ButtonPress-1>", '-DOWN_MOVE')
    window['-DOWN'].bind("<ButtonRelease-1>", '-DOWN_STOP')

    capture_state_flag = 0
    calb_flag = 0
    frame_counter = 0
    all_fr_cnt = 0
    W = np.zeros((1024, 1024), 'int')
    n_frames = 0
    fall = deque(W)

    window['-WATERFALL'].update(data=cv2.imencode('.png', W)[1].tobytes())
    window['-SONY'].update(data=cv2.imencode('.png', W)[1].tobytes())
    distance_arr_cnt = 0
    cap = cv2.VideoCapture(0)

    while True:
        if capture_state_flag == 0:
            ret, frame = cap.read()
            if frame is None:
                width = 1280
                height = 720
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

            elif event == '-MOVE_TO_START_POSITION':
                ptr.move_to(values['-START_POS_VALUE'][0:2], values['-START_POS_VALUE'][2:])

                ptr_sector_moving = 360
                ptr_hex_value = 158
                ptr_per_value = ptr_sector_moving / ptr_hex_value

                values_for_lidar_hex = int(values['-END_POS_VALUE'][0:2], 16) - int(values['-START_POS_VALUE'][0:2], 16)
                print('vfl_hex = ', values_for_lidar_hex)

                values_for_lidar_deg = int(values_for_lidar_hex * ptr_per_value)
                print('values_for_lidar_deg = ', values_for_lidar_deg)

                curr_lidar_value = 180 - values_for_lidar_deg
                print('curr lidar value = ', curr_lidar_value)

                lidar_deg_per_value = 360 / 1024  # 0.3515625
                print('lidar_deg_per_value = ', lidar_deg_per_value)

                points_for_lidar = int(values_for_lidar_deg / lidar_deg_per_value)
                print('points_for_lidar = ', points_for_lidar)

            elif event == '-MOVE_TO_END_POSITION':
                ptr.move_to(values['-END_POS_VALUE'][0:2], values['-END_POS_VALUE'][2:])
            elif event == '-SET_START':
                pos = ptr.get_current_position()
                window['-START_POS_VALUE'].update(value=pos[0] + pos[1])
            elif event == '-SET_END':
                pos = ptr.get_current_position()
                window['-END_POS_VALUE'].update(value=pos[0] + pos[1])

            ###########################################################################################################
            ############################## Lidar Ouster OS1 - 128U ####################################################
            ###########################################################################################################

            elif event == '-GET_PLY':
                n_frames, distance_arr = lidar.Lidar(curr_lidar_value).create_ply(
                    main_path + r'\\' + values['-DATA_NAME'])
                print(n_frames, distance_arr)

            ###########################################################################################################
            ############################## RGB Camera Sony FCB  #######################################################
            ###########################################################################################################

            elif event == '-ZOOM':
                zoom.comm(visca_rgb.ZOOM_SETTINGS[int(values['-ZOOM'])])

            ###########################################################################################################
            ############################## Capture HS camera  #########################################################
            ###########################################################################################################

            elif event == '-CAPTURE':
                capture_state_flag = 1
                alpha_specim = 0.0371
                w = int(values['-FPS']) * alpha_specim
                current_min_speed = ''
                current_min_delta = 1

                for hex, speed in scanner.scanner_speed.items():
                    delta_w_min = abs(w - float(speed))
                    if delta_w_min < current_min_delta:
                        current_min_speed = hex
                        current_min_delta = delta_w_min
                hex_w = current_min_speed
                print('vehicle for platform:  ', hex_w)
                gen = create_gen(int(values['-EXPOS_VALUE']), n_frames, values['-DATA_NAME'], specim,
                                 int(values['-FPS']), int(values['-SET_END']))

            elif event == '-LIVE':
                print('[INFO] Moving to calibration position...')
                print('[INFO] Start calibration')
                calb_flag = 1
                gen_calb = create_gen(int(values['-EXPOS_VALUE']), 0, '', specim, int(values['-FPS']))
            elif event == '-STOP_LIVE':
                calb_flag = 0
                print('[INFO] Stop calibration')

            #######################################################################################################
            ########################## CAPTURE GENERATORS #########################################################
            #######################################################################################################
            #print(ptr.get_current_position())
            if calb_flag == 1:
                a = next(gen_calb)

                if len(fall) == 1024:
                    fall.popleft()
                fall.append(a[:, 20] / 20)
                imgbytes4 = cv2.imencode('.png', np.rot90(np.array(fall)))[1].tobytes()
                window['-WATERFALL'].update(data=imgbytes4)

            try:

                if capture_state_flag == 1:
                    window['-SONY'].update(data=cv2.imencode('.png', W)[1].tobytes())
                    ptr.move_right(str(hex_w))
                    a = next(gen)
                    if len(fall) == 1024:
                        fall.popleft()
                    fall.append(a[:, 20] * 20)
                    imgbytes4 = cv2.imencode('.png', np.rot90(np.array(fall)))[1].tobytes()
                    window['-WATERFALL'].update(data=imgbytes4)
                    frame_counter += 1
                    if frame_counter == 9:
                        frame_counter = 0
                        distance_arr_cnt += 1
                    all_fr_cnt += 1
            except StopIteration:
                print("Stop iter")
                capture_state_flag = 0
                frame_counter = 0
                specim.close_ia()
                ptr.stop()
                print('[INFO] Stop capturing')
        except Exception as error:
            print(error)


if __name__ == '__main__':
    specim = hspec_camera.Camera()
    ptr = scanner.Ptr()
    App()