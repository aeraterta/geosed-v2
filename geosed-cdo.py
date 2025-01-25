# For Sensors Libraries
from lib.sensors import getSensor
import cv2
import numpy as np

# For Data Logging Libraries
import threading
import os
import calendar
import csv
import sys
import time

sensor = getSensor()
h = []

with open('/home/pi/Desktop/RiverMonitor/sub/credentials/thread_val.txt') as f:
    for i in f:
        h.append(i)

threadTimer_log = int(h[1])  # Logs Sensors Data to USB and to Cloud Every n (900) secs / 15 mins

# --------DATA LOGGING----------------#
save_path = '/home/pi/Desktop/RiverMonitor/logged_data/'
file_name = 'sensors_data_BKDN.csv'
comfile = os.path.join(save_path, file_name)

file = open(comfile, 'w')
file.write('Time,Date,Water Level,Water Flow Rate,River Discharge,Panel Temperature,Panel Humidity,CPU Temperature,CPU Usage,CPU Clock Speed\n')
file.close()

# ---------CLOUD UPLOADING------------#
API_token = 'BBFF-9MYyS6VdQHNtfoLpazYNEZmAjO8KJh'

wlevel_id = '621879d1a12f9d383ed9c84b'
wflow_id = '621879d589a2f840b3a5c929'
rdischarge_id = '621879e089a2f848efb280c2'

phum_id = '621879d589a2f848efb280c0'
ctemp_id = '621879d6a12f9d383ed9c84c'