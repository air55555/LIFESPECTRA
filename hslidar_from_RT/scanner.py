import socket

#### Speed 0 - 9D
#### PAN 0 - 157

scanner_speed = {
    '00': 0,
    '02': 0.122901332,
    '03': 0.135453838,
    '04': 0.149244141,
    '05': 0.164443858,
    '06': 0.18121377,
    '07': 0.19970621,
    '08': 0.220039216,
    '09': 0.242505404,
    '0A': 0.267204639,
    '0B': 0.294448902,
    '0C': 0.324489492,
    '0D': 0.357579899,
    '0E': 0.394007151,
    '0F': 0.434113089,
    '10': 0.47838243,
    '11': 0.527145813,
    '12': 0.580813785,
    '13': 0.640080792,
    '14': 0.7051606,
    '15': 0.777037673,
    '16': 0.865105951,
    '17': 0.943534691,
    '18': 1.039546065,
    '19': 1.145522756,
    '1A': 1.261781004,
    '1B': 1.390321048,
    '1C': 1.532240902,
    '1D': 1.68822277,
    '1E': 1.859619398,
    '1F': 2.048608938,
    '20': 2.256770311,
    '21': 2.487149726,
    '22': 2.738871433,
    '23': 3.016742923,
    '24': 3.324867236,
    '25': 3.660582643,
    '26': 4.034291478,
    '27': 4.28556123,
    '28': 4.892700363,
    '29': 5.389463599,
    '2A': 5.934326784,
    '2B': 6.530730716,
    '2C': 7.191514013,
    '2D': 7.902015014,
    '2E': 8.692712609,
    '2F': 9.589004608,
    '30': 10.56524036,
    '31': 11.60466766,
    '32': 12.77048599,
    '33': 14.05261925,
    '34': 15.46391753,
    '35': 17.00118064,
    '36': 18.70712949,
    '37': 20.49880424,
    '38': 22.57761054,
    '39': 24.87218461,
    '3A': 27.25001892,
    '3B': 29.8136646,
    '3C': 32.66787659,
    '3D': 36.05769231,
    '3E': 39.23278117,
    '3F': 43.01075269

}


class UdpClient():
    def __init__(self):
        self._port = 6000
        self._host = '192.168.0.93'

    def _client_up(self, cmd):
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        _serverAddress = (self._host, self._port)
        UDPServerSocket.sendto(bytes.fromhex(cmd), _serverAddress)
        if '51' and '52' in cmd:
            reply = UDPServerSocket.recv(8192)
            rep = bytes.hex(reply)
            UDPServerSocket.close()
            return [rep[8:10], rep[10:12]]


class Ptr():
    def __init__(self):
        self._synch_byte = 'FF'
        self._address = '01'
        self._command1 = '00'
        self._sock = UdpClient()

    def _cheksum256(self, _cmd):
        dec_cs = (int(_cmd[0], 16) + int(_cmd[1], 16) + int(_cmd[2], 16) + int(_cmd[3], 16) + int(_cmd[4], 16))
        if dec_cs > 256:
            dec_cs = dec_cs - 256
        if len(hex(dec_cs)[2:]) < 2:
            return '0' + hex(dec_cs)[2:]
        else:
            return hex(dec_cs)[2:]

    def _construct_cmd(self, _command2, _pan_speed, _tilt_speed):
        bytes = [self._address, self._command1, _command2, _pan_speed, _tilt_speed]
        cs = self._cheksum256(bytes)
        com = f'{self._synch_byte} {self._address} {self._command1} {_command2} {_pan_speed} {_tilt_speed} {cs}'
        return com

    def move_right(self, speed):
        if len(speed) == 1:
            speed = '0' + speed
        cmd = self._construct_cmd('02', f'{speed}', '00')
        return self._sock._client_up(cmd)

    def stop(self):
        cmd = self._construct_cmd('02', '00', '00')
        return self._sock._client_up(cmd)

    def move_left(self):
        cmd = self._construct_cmd('04', '32', '00')
        return self._sock._client_up(cmd)

    def move_up(self):
        cmd = self._construct_cmd('08', '30', '30')
        return self._sock._client_up(cmd)

    def move_down(self):
        cmd = self._construct_cmd('10', '30', '30')
        return self._sock._client_up(cmd)

    def get_current_position(self):
        cmd = self._construct_cmd('51', '00', '00')
        return self._sock._client_up(cmd)

    def move_to(self, hh, ll):
        cmd = self._construct_cmd('71', f'{hh}', f'{ll}')
        return self._sock._client_up(cmd)
