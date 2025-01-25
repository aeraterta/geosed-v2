''' PLAN A MAIN SYSTEM '''
''' Partnered with A.1_GeoSED_CDO.py '''
''' ISOLATED FREA FROM MAIN SYSTEM '''


# River Monitoring Libraries Libraries
from lib.waterlevel import lidarRead
import busio
import cv2
import numpy as np
from lib.tracker import *

# CPU Status Libraries
from gpiozero import CPUTemperature
import psutil

# DHT22 Libraries
import board
import adafruit_dht

# Data Logging Libraries
import os
import csv
import time

# Libraries For Testing
import random


# ------------initializing and assigning---------------#
lidar = lidarRead()
connected = lidar.connect(1)
dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)
threadDelay = 5
counter = 0
recent = 0

# ------ OPENING REAL-TIME WATER LEVEL DATA ------ #
wtrlvl_src_path = '/home/pi/Desktop/RiverMonitor/logged_data/'
wtrlvl_src_name = 'realtime_wtrlvl_data_BKDN.csv'
wtrlvl_src = os.path.join(wtrlvl_src_path, wtrlvl_src_name)

# ------ OPENING REAL-TIME FLOW RATE DATA ------ #
src_path = '/home/pi/Desktop/RiverMonitor/logged_data/'
src_name = 'realtime_wtrflw_data.csv'
src = os.path.join(src_path, src_name)

# --------REAL-TIME DATA LOGGING WATER LEVEL----------------#
rt_wtrlvl_save_path = '/home/pi/Desktop/RiverMonitor/logged_data/'
rt_wtrlvl_file_name = 'realtime_wtrlvl_data_BKDN.csv'
rt_wtrlvl_comfile = os.path.join(rt_wtrlvl_save_path, rt_wtrlvl_file_name)

file = open(rt_wtrlvl_comfile, 'w')
file.write('Time,Water Level\n')
file.close()

class getSensor():

    def getRiverDischarge(self):
        water_level = self.getwaterLevel()
        width = 103.3550
        if water_level is not None:
            river_x_section_area = width * water_level
            water_flow = self.getWaterFlow()
            if water_flow is not None:
                river_discharge = river_x_section_area * water_flow
                river_discharge_conv = round(river_discharge, 2)
                return river_discharge_conv

    def getcpuTemp(self):
        cpu = CPUTemperature()
        cpu_temp_f = cpu.temperature
        cpu_temp = round(cpu_temp_f, 2)
        return cpu_temp

    def getcpuSpeed(self):
        cpu_cs_f = int(open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq").read()) / 1000
        cpu_cs = round(cpu_cs_f, 2)
        return cpu_cs

    def getcpuUsage(self):
        cpu_usage_f = psutil.cpu_percent()
        cpu_usage = round(cpu_usage_f, 2)
        return cpu_usage

    def CommenceWLE(self):
            # Runtime Error Prevention
            # Water Level Reading
            datum = 14.9149
            try:
                sensor_data_cm = lidar.getDistance()
            except RuntimeError as error:
                sensor_data_cm = lidar.getDistance()
                pass

            if sensor_data_cm is not None:
                sensor_data_m = sensor_data_cm / 100
                water_line = round(sensor_data_m, 4)
                water_level = float(datum) - float(water_line)
                if water_level < 14:
                    self.rt_wtrlvl(water_level)

    def getwaterLevel(self):
        # Reading the Real-time Water Flow Rate Data
        wtrlvl_data = []

        # Reads Flow Rate data on the realtime_flowrate_data csv file
        with open(wtrlvl_src, 'r') as csv_file:
            csv_reader = csv.reader(csv_file.readlines()[-10:], delimiter=',')

            next(csv_reader)
            for wtrlvl in csv_reader:
                wtrlvl_data.append(float(wtrlvl[1]))

        if len(wtrlvl_data) != 0:
            if wtrlvl_data is not None:
                ave = sum(wtrlvl_data) / len(wtrlvl_data)
                wtrlvl_data = round(ave, 2)
                return wtrlvl_data

    def getdhtTemp(self):

        # Checksum Error Prevention
        try:
            Tval = dhtDevice.temperature
        except RuntimeError as error:
            Tval = dhtDevice.temperature
            pass

        if Tval is not None:
            dht_temp = round(Tval, 2)
            return dht_temp

    def getdhtHum(self):
        # Checksum Error Prevention
        # Panel Humidity Reading
        try:
            Hval = dhtDevice.humidity
        except RuntimeError as error:
            Hval = dhtDevice.humidity
            pass

        if Hval is not None:
            dht_hum = round(Hval, 2)
            return dht_hum

    def getWaterFlow(self):
        # Reading the Real-time Water Flow Rate Data
        wtrflw_data = []

        # Reads Flow Rate data on the realtime_flowrate_data csv file
        with open(src, 'r') as csv_file:
            csv_reader = csv.reader(csv_file.readlines()[-10:], delimiter=',')

            next(csv_reader)
            for wtrflw in csv_reader:
                wtrflw_data.append(float(wtrflw[1]))

        # print("waterflow from lists: ", wtrflw_data)
        if len(wtrflw_data) != 0:
            if wtrflw_data is not None:
                a_speed_ms_raw = sum(wtrflw_data) / len(wtrflw_data)
                a_speed_ms = (a_speed_ms_raw * 0.9567) + 0.0426 + 0.0382
                wtrflw_data = round(a_speed_ms, 2)
                return wtrflw_data

    def rt_wtrlvl (self, wtr_lvl):
            # Data Logging Algorithm
            file = open(rt_wtrlvl_comfile, 'a')
            file.write(time.strftime('%H:%M:%S') + ',' + str(wtr_lvl) + '\n')
            file.close()
            time.sleep(0.5)
