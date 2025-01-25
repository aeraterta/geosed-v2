''' ISOLATED LIDAR TEST IF IT READS PROPER DATA AND FIXES RUNTIME ERROR '''
''' DATA LOGGING INCLUDED '''

# River Monitoring Libraries
from lib.waterlevel import lidarRead

import busio
import board

# Data Logging and Threading
import time
import csv
import threading
import os

lidar = lidarRead()
connected = lidar.connect(1)

# --------REAL-TIME DATA LOGGING----------------#
rt_save_path = '/home/pi/Desktop/RiverMonitor/logged_data/'
rt_file_name = 'A.1_wtrlvl_data_.csv'
comfile = os.path.join(rt_save_path, rt_file_name)

file = open(comfile, 'w')
file.write('Time,Date,Water Level\n')
file.close()

threadTimer_log = 5


def getwaterLevel():
    threading.Timer(threadTimer_log, getwaterLevel).start()

    # Runtime Error Prevention
    # Water Level Reading
    try:
        sensor_data_cm = lidar.getDistance()
        time.sleep(0.5)
    except RuntimeError as error:
        sensor_data_cm = lidar.getDistance()
        time.sleep(0.5)
        pass

    if sensor_data_cm is not None:
        datum = 14.8518
        sensor_data_ms = sensor_data_cm / 100
        sensor_data_m = round(sensor_data_ms, 3)
        print("Uncalibrated Water Level (m): ", sensor_data_m)

        water_level = datum - sensor_data_m
        print("Calibrated Water Level (m): ", water_level)

        # Data Logging Algorithm
        file = open(comfile, 'a')
        file.write(time.strftime('%H:%M:%S,%d/%m/%Y') + ',' + str(water_level) + '\n')
        file.close()

        time.sleep(2.0)
        return water_level


getwaterLevel()
