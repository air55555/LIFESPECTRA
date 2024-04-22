from ouster import client
from contextlib import closing
import matplotlib.pyplot as plt
from more_itertools import nth
import numpy as np
from statistics import mean
import sys


class Lidar:
    def __init__(self, L_value):
        self._hostname = '192.168.0.15'
        self._config = client.SensorConfig()
        self._config.udp_port_lidar = 7502
        self._config.udp_port_imu = 7503
        self._config.operating_mode = client.OperatingMode.OPERATING_NORMAL
        self._L_value = L_value
        self._config.azimuth_window = (int(L_value)*1000, 180000)
        self._config.lidar_mode = client.LidarMode.MODE_2048x10
        client.set_config(self._hostname, self._config, persist=True, udp_dest_auto = True,)

    def create_ply(self, path):
        source = client.Sensor(self._hostname, 7502, 7503)
        info = source.metadata

        with closing(client.Scans(source)) as scans:
            scan = nth(scans, 50)

        range_field = scan.field(client.ChanField.RANGE)
        range_img = client.destagger(info, range_field)
        range_img2 = range_img.copy()
        a = []

        for i,z in enumerate(range_img[:, 1024:2048]):
            if i == 0:
                a = range_img[i, 1024:2048]
            else:
                a += range_img[i, 1024:2048]

        a = a/128
        new_arr = []
        for i, k in enumerate(a):
            if a[i] == 0:
                n_frames = len(new_arr)*4
                break
            new_arr.append([9, int(0.0006725*(a[i]-100)/100*20*180/3.14)])

        np.savetxt(path + "foo.csv", range_img2[:, 1024:1024+i], delimiter=",")
        plt.imshow(range_img2[:, 1024:1024+i], resample=False)
        plt.show()

        return n_frames, new_arr