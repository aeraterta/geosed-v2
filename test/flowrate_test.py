
import cv2
import time
import numpy as np
from lib.tracker import *
import os
import time


# --------REAL-TIME DATA LOGGING----------------#
rt_save_path = '/home/pi/Desktop/RiverMonitor/logged_data'
#rt_save_path = 'C:/Users/janne/Desktop/RiverMonitor2/logged_data/'
rt_file_name = 'realtime_wtrflw_data.csv'
rt_comfile = os.path.join(rt_save_path, rt_file_name)

file = open(rt_comfile, 'w')
file.write('Time,Water Flow Rate\n')
file.close()

# Create Motion Tracker
tracker = EuclideanDistTracker()

# Area for Time Start & End (ROI)
area_1 = [(20, 400), (20, 420), (832, 420), (832, 400)]
area_2 = [(594, 50), (594, 90), (994, 90), (994, 50)]  # Dummy
area_3 = [(20, 440), (20, 460), (832, 460), (832, 440)]

#area_1 = [(140, 140), (140, 160), (712, 160), (712, 140)]
#area_2 = [(594, 50), (594, 90), (994, 90), (994, 50)]  # Dummy
#area_3 = [(140, 200), (140, 220), (712, 220), (712, 200)]

#area_1 = [(150, 150), (150, 170), (702, 170), (702, 150)]
#area_2 = [(594, 50), (594, 90), (994, 90), (994, 50)]  # Dummy
#area_3 = [(150, 190), (150, 210), (702, 210), (702, 190)]

#area_1 = [(100, 100), (100, 120), (752, 120), (752, 100)]
#area_2 = [(594, 50), (594, 90), (994, 90), (994, 50)]  # Dummy
#area_3 = [(100, 160), (100, 140), (752, 140), (752, 160)]

#area_1 = [(20, 219), (20, 239), (420, 239), (420, 219)]
#area_2 = [(594, 50), (594, 90), (994, 90), (994, 50)]  # Dummy
#area_3 = [(20, 279), (20, 259), (420, 259), (420, 279)]

# Points Entering Area 1
points_entering = {}
points_elapsed_time = {}
a_speed_ms_lists = []

class getSensor:

    def getWaterFlow(self, roi, mask):

        for i, area in enumerate([area_1, area_2, area_3]):
            if i == 1:
                continue

            cv2.polylines(roi, [np.array(area, np.int32)], True, (15, 220, 10), 6)

        # 1. Object Detection
        _, thresh = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        blur = cv2.GaussianBlur(thresh, (5, 5), 0)
        dilated = cv2.dilate(blur, None, iterations = 3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        detections = []

        for cnt in contours:
            # Calculate Area and Remove Small Elements
            area = cv2.contourArea(cnt)
            if area > 3:
                #cv2.drawContours(roi, [cnt], -1, (0, 255, 0), 2)
                x, y, w, h = cv2.boundingRect(cnt)
                detections.append([x, y, w, h])

########################################### ALGORITHM ABOVE IS CLEARED #####################################################

        # 2. Object Tracking
        boxes_ids = tracker.update(detections)
        for box_id in boxes_ids:
            x, y, w, h, id = box_id
            cx = int((x + x + w) / 2)
            cy = int((y + y + h) / 2)
            #print("Cx: ", cx)
            #print THIS AREA WORKS

            result1 = cv2.pointPolygonTest(np.array(area_1, np.int32), (int(cx), int(cy)), False)
            if result1 >= 0:
                points_entering[id] = time.time()

            if id in points_entering:
                result2 = cv2.pointPolygonTest(np.array(area_3, np.int32), (int(cx), int(cy)), False)

                if result2 >= 0:
                    elapsed_time = time.time() - points_entering[id]

                    if id not in points_elapsed_time:
                        points_elapsed_time[id] = elapsed_time

                    if id in points_elapsed_time:
                        elapsed_time = points_elapsed_time[id]

                    # Calculate Flow Rate
                    distance = 0.3
                    speed_ms = float(distance / elapsed_time) if elapsed_time != 0 else 0

                    # Calculate Average of all Points
                    a_speed_ms_lists.append(round(speed_ms, 4))
                    a_speed_ms = sum(a_speed_ms_lists) / len(a_speed_ms_lists)
                    wtrflw = a_speed_ms
                    self.rt_data_logging(wtrflw)

                    print("Flow Rate: " + str(wtrflw) + "m/s")
                    print("Flow Rate Lists: " + str(a_speed_ms_lists) + "m/s")
                    #cv2.putText(roi, "Average Flow: " + str(round(a_speed_ms, 2)) + "m/s", (x, y - 15), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                    #cv2.putText(roi, str(a_speed_ms_lists), (x, y - 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                    #cv2.circle(roi, (cx, cy), 5, (255, 0, 0), -1)
                    # cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    return wtrflw

        #cv2.imshow("ROI ON SUB-SCRIPT", roi)
        #cv2.imshow("Mask", mask)
        #cv2.imshow("Blur", blur)
        cv2.imshow("Dilated on Subscript", dilated)
        cv2.imshow("ROI", roi)
        #print("Hellow World!")

    def rt_data_logging(self, water_flow):
        # Data Logging Algorithm
        file = open(rt_comfile, 'a')
        file.write(time.strftime('%H:%M:%S') + ',' + str(water_flow) + '\n')
        file.close()
        time.sleep(1.0)




