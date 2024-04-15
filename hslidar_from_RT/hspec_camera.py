import csv
import time
import harvesters
from harvesters.core import Harvester, ImageAcquirer
from spectral import *
import numpy as np
import cv2
import h5py
from datetime import datetime as dt
import os
from typing import NoReturn, Iterator
import scanner

class Camera:
    def __init__(self):
        self._ia = None
        self._cti_file = r"C:\Program Files\MATRIX VISION\mvIMPACT Acquire\bin\x64\mvGenTLProducer.cti"
        self._h = Harvester()
        self._h.add_file(self._cti_file)
        self._h.update()

    @staticmethod
    def save_to_envi(image_arr: np.ndarray, dir_name: str, name_add) -> NoReturn:
        if dir_name == name_add:
            name_add = 'image'
        envi.save_image(f'Datasets/{dir_name}/{name_add}.hdr', image_arr)#, metadata={'wavelength': wavelenghts.waves})

    def shutter(self, state):
        # -1 close
        # 1 open
        if state == 1:
            self._ia.remote_device.node_map.MotorShutter_PulseRev.value = 201
            self._ia.remote_device.node_map.MotorShutter_PulseRev.value = 200
        elif state == -1:
            self._ia.remote_device.node_map.MotorShutter_PulseFwd.value = 205
            self._ia.remote_device.node_map.MotorShutter_PulseFwd.value = 204
        else:
            print('[ERROR] Something wrong with shutter value')

    def camera_params(self, EXP: int, FPS: int) -> NoReturn:
        self._ia.remote_device.node_map.ExposureTime.value = EXP
        self._ia.remote_device.node_map.AcquisitionFrameRate.value = FPS

    def close_camera(self) -> NoReturn:
        self._h.reset()

    @staticmethod
    def frame_stitching(f: h5py, frames: int):
        ptr = scanner.Ptr()
        ptr.stop()
        print('[INFO] Stitching frames')
        image_arr = []
        for key in range(frames):
            prom = (np.rot90(f[str(key)][:].reshape(224, 1024)))[:, np.newaxis, :]
            image_arr = np.concatenate((image_arr, prom), axis=1) if f[str(key)].name != '/0' else prom
        return image_arr

    def calibration(self, EXP: int, FPS) -> Iterator[np.ndarray]:
        self._ia = self._h.create(0)
        self.camera_params(EXP, FPS)
        self._ia.start()
        self.shutter(1)
        while True:
            with self._ia.fetch() as buffer:
                component = buffer.payload.components[0]
                Data = component.data
                frame_2d = Data.reshape(component.height, component.width)
                fr = (np.rot90(frame_2d))
            yield fr

    def capturing(self, EXP: int, frames: int, data_name: str, FPS: int) -> Iterator[np.ndarray]:
        dir_name = data_name if data_name else dt.now().strftime("%H_%M")
        if not os.path.exists(os.getcwd() + fr'\Datasets\{dir_name}'):
            os.mkdir(os.getcwd() + fr'\Datasets\{dir_name}')
        h5_file = h5py.File(fr"{os.getcwd()}\Datasets\{dir_name}\{'POH'}.hdf5", "w")
        self._ia = self._h.create(0)
        self.shutter(1)
        self.camera_params(EXP, FPS)
        self._ia.start()
        frames_number = range(frames)
        for frame in frames_number:
            with self._ia.fetch() as buffer:
                component = buffer.payload.components[0]
                Data = component.data
                h5_file.create_dataset(f"{frame}", data=Data)
                frame_2d = Data.reshape(component.height, component.width)
                fr = (np.rot90(frame_2d))
            if frame != frames_number:
                yield fr

        image_arr = self.frame_stitching(h5_file, frames)
        h5_file.close()
        self.save_to_envi(image_arr, dir_name, 'tuy')

    def close_ia(self):
        self._ia.stop()
        self._ia.destroy()
