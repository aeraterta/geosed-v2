# FINAL DATA LOGGING WITH THREADING OF THE FLOW RATE DATA

from flowrate_test import getSensor
import cv2
import csv
import os
import time
import threading

ThreadTimer = 5
ThreadTimer_log = 5
sensor = getSensor()
object_detector = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=40)

def RunWaterFlowAlgo():
    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture("test45.mp4")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 852)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        
        #height, width, _ = frame.shape
        #print(height, width)

        #roi = frame[100: 380, 100: 752]
        mask = object_detector.apply(frame)

        water_flow = sensor.getWaterFlow(frame, mask)

        print("Average Flow Rate Main Script: ", water_flow)
        # cv2.imshow("Frame", frame)
        # cv2.imshow("ROI", ROI)

        key = cv2.waitKey(30)
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    RunWaterFlowAlgo()







