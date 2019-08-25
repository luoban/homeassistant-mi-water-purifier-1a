# import os
# import time
import datetime
import math
import logging
from miio import Device, DeviceException

host = '192.168.123.67'
token = 'afe90c5eac1b6445e82e9960bf317bf6'
#host = '192.168.123.90'
#token = '524a33744844594b4258433175445453'
AVAILABLE_PROPERTIES_COMMON = [
   'tds_out', 
   'temperature', 
   'f1_totalflow', 
   'f1_totaltime', 
   'f1_usedflow',
   'f1_usedtime', 
   'f2_totalflow', 
   'f2_totaltime', 
   'f2_usedflow', 
   'f2_usedtime',
   'run_status', 
   'rinse', 
   'tds_warn_thd', 
   'tds_out_avg'
] 
def main():
    print('this message is from main function')
    device = Device(host, token)
    data = {}
    print('send get prop')
#    params = {"tds_out", "temperature", "f1_totalflow", "f1_totaltime", "f1_usedflow", "f1_usedtime", "f2_totalflow", "f2_totaltime", "f2_usedflow", "f2_usedtime", "run_status", "rinse", "tds_warn_thd", "tds_out_avg" }
    properties = AVAILABLE_PROPERTIES_COMMON
    _props_per_request = 1
    _props = properties.copy()
    values = []
    while _props:
        status = device.send("get_prop", _props[:_props_per_request])
        _props[:] = _props[_props_per_request:]
        print('send get prop finished ',status)

if __name__ == '__main__':
    main()
    # print(__name__)

