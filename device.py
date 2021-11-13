import dataclasses as d
import subprocess, re
import adi
from adiutil.static import *

@d.dataclass
class Device:

    serial: str
    uri_usb: str
    name: str = None
    __pluto: adi.Pluto = None

    def __post_init__(self):
        if self.name == None:
            self.name = f"[{self.uri_usb}](serial={self.serial})"

    """
    adi.Plutoは初回呼び出し時に初期化されます
    2回目以降はキャッシュを返します
    """
    def get_pluto(self):
        if self.__pluto != None:
            return self.__pluto
        pluto = adi.Pluto(self.uri_usb)
        # set init parameter
        pluto.tx_lo = DEFAULT_TX_LO
        pluto.rx_lo = DEFAULT_RX_LO
        pluto.tx_rf_bandwidth = DEFAULT_TX_BW
        pluto.rx_rf_bandwidth = DEFAULT_RX_BW
        pluto.sample_rate = SAMPLE_RATE
        self.__pluto = pluto
        return pluto

class DeviceList:

    def __init__(self):
        res = subprocess.run(R'iio_info -S', shell=True, stdout=subprocess.PIPE)
        lines = res.stdout.decode('utf-8').splitlines()
        adress_re = re.compile(r'\d+:.*')
        serial_re = re.compile(r'[\d|a-f]{34}')
        usb_re = re.compile(r'usb:\d+\.\d+\.\d+')
        devices = []
        for line in lines:
            line = line.strip()
            if not adress_re.fullmatch(line):
                continue
            serial = serial_re.search(line)
            uri_usb = usb_re.search(line)
            if serial == None or uri_usb == None:
                continue
            devices.append(Device(serial.group(), uri_usb.group()))
        self.devices = devices
    
    def find(self, serial: str) -> Device:
        for device in self.devices:
            if device.serial == serial:
                return device
        raise Exception("device not found")

    def all(self, excludes=[]):
        filterd = []
        for device in self.devices:
            if not device.serial in excludes:
                filterd.append(device)
        return filterd

# print(DeviceList().all())