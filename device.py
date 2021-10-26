import dataclasses as d
import subprocess, re
import adi

@d.dataclass
class Device:

    serial: str
    uri_usb: str

    def create_pluto(self):
        return adi.Pluto(self.uri_usb)

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