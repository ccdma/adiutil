import dataclasses as d
import subprocess, re
import adi
from adiutil.static import *

@d.dataclass
class Device:

    serial: str
    uri_usb: str
    name: str = None
    __sdr: adi.Pluto = None

    def __post_init__(self):
        if self.name == None:
            self.name = f"[{self.uri_usb}](serial={self.serial})"

    @property
    def serial_short(self):
        return self.serial[-5:]

    """
    adi.Plutoは初回呼び出し時に初期化されます
    2回目以降はキャッシュを返します
    """
    def get_pluto(self, init=False):
        if self.__sdr != None:
            return self.__sdr
        sdr = adi.Pluto(self.uri_usb)
        # set init parameter
        if init:    # 受信にに使用する場合、sdr.txの設定はしないほうがよい
            sdr.tx_lo = DEFAULT_TX_LO
            sdr.rx_lo = DEFAULT_RX_LO
            sdr.tx_rf_bandwidth = DEFAULT_TX_BW
            sdr.rx_rf_bandwidth = DEFAULT_RX_BW
            sdr.sample_rate = SAMPLE_RATE
        self.__sdr = sdr
        return sdr

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
            # 文字列後方一致
            if device.serial[-len(serial):] == serial:
                return device
        raise Exception("device not found")

    def all(self, excludes=[]):
        filterd = []
        for device in self.devices:
            if not device.serial in excludes:
                filterd.append(device)
        return filterd

# print(DeviceList().all())