import sys
import threading
import time
import logging
import serial
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide2.QtCore import Qt
import queue

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Global variables for sensor averages
water_level_avg = 0.0
water_flow_avg = 0.0
river_discharge_avg = 0.0
dht_temp_avg = 0.0
dht_hum_avg = 0.0
avg_count = 0

# Global variables for CPU readings
cpu_temp_last = 0.0
cpu_usage_last = 0.0
cpu_speed_last = 0.0

# Flags to indicate thread termination
terminate_program = False
processing = False

# Interval for data logging (in seconds)
threadTimer_log = 60

# File for logging data
comfile = "data_log.csv"

# UART Configuration
SERIAL_PORT = "/dev/serial0"  # Default UART port on Raspberry Pi
BAUD_RATE = 9600  # Baud rate for UART communication

# Queue for sending data to UART thread
uart_queue = queue.Queue()

# Mock sensor class
class Sensor:
    def getwaterLevel(self):
        return 1.23

    def getWaterFlow(self):
        return 0.45

    def getRiverDischarge(self):
        return 12.34

    def getdhtTemp(self):
        return 25.6

    def getdhtHum(self):
        return 60.5

    def getcpuTemp(self):
        return 55.3

    def getcpuUsage(self):
        return 35.7

    def getcpuSpeed(self):
        return 3.2

sensor = Sensor()

# Function to compute and update averages for the required sensors
def update_sensor_averages():
    global water_level_avg, water_flow_avg, river_discharge_avg, dht_temp_avg, dht_hum_avg, avg_count

    # Retrieve sensor data
    water_level = sensor.getwaterLevel()
    water_flow = sensor.getWaterFlow()
    river_discharge = sensor.getRiverDischarge()
    dht_temp = sensor.getdhtTemp()
    dht_hum = sensor.getdhtHum()

    # Update averages
    avg_count += 1
    water_level_avg = (water_level_avg * (avg_count - 1) + water_level) / avg_count
    water_flow_avg = (water_flow_avg * (avg_count - 1) + water_flow) / avg_count
    river_discharge_avg = (river_discharge_avg * (avg_count - 1) + river_discharge) / avg_count
    dht_temp_avg = (dht_temp_avg * (avg_count - 1) + dht_temp) / avg_count
    dht_hum_avg = (dht_hum_avg * (avg_count - 1) + dht_hum) / avg_count

    logger.info(f"Updated averages: WaterLevel={water_level_avg:.2f}, WaterFlow={water_flow_avg:.2f}, "
                f"RiverDischarge={river_discharge_avg:.2f}, DHTTemp={dht_temp_avg:.2f}, DHTHum={dht_hum_avg:.2f}")

# Sensor checking thread (runs every 5 seconds)
def sensor_check():
    while not terminate_program:
        update_sensor_averages()
        time.sleep(5)

# Data logging thread
def data_log():
    global processing, cpu_temp_last, cpu_usage_last, cpu_speed_last

    while not terminate_program:
        if processing:
            logger.info("Skipping this execution to avoid overlap.")
            time.sleep(1)
            continue

        processing = True
        thread_start_time = time.time()

        try:
            # Retrieve the last CPU values
            cpu_temp_last = sensor.getcpuTemp()
            cpu_usage_last = sensor.getcpuUsage()
            cpu_speed_last = sensor.getcpuSpeed()

            # Log data
            log_data = (f"{time.strftime('%H:%M:%S,%d/%m/%Y')},{water_level_avg:.2f},{water_flow_avg:.2f},"
                        f"{river_discharge_avg:.2f},{dht_temp_avg:.2f},{dht_hum_avg:.2f},"
                        f"{cpu_temp_last:.2f},{cpu_usage_last:.2f},{cpu_speed_last:.2f}\n")

            try:
                # Write to CSV
                with open(comfile, 'a') as file:
                    file.write(log_data)
                    logger.info("Data logged successfully.")

                # Send data to UART via queue
                uart_queue.put(log_data)
            except IOError as e:
                logger.error(f"File write error: {e}")

        finally:
            processing = False

        # Wait for the next execution
        while time.time() - thread_start_time < threadTimer_log and not terminate_program:
            time.sleep(1)

# UART communication thread
def uart_thread():
    try:
        # Initialize UART
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        logger.info(f"Connected to UART at {SERIAL_PORT} with baud rate {BAUD_RATE}")

        while not terminate_program:
            # Send data from queue
            if not uart_queue.empty():
                data_to_send = uart_queue.get()
                ser.write(data_to_send.encode())
                logger.info(f"Sent data to UART: {data_to_send.strip()}")

            # Read data from UART
            if ser.in_waiting > 0:
                received_data = ser.readline().decode('utf-8').strip()
                logger.info(f"Received from UART: {received_data}")

            time.sleep(1)  # Avoid busy-waiting
    except serial.SerialException as e:
        logger.error(f"UART error: {e}")

# PySide2 GUI for controlling threads
class ThreadController(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thread Management")
        self.setGeometry(300, 300, 400, 200)

        # Layout and UI Elements
        self.layout = QVBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.status_label = QLabel("Status: Not running")
        self.stop_button.setDisabled(True)

        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.stop_button)
        self.layout.addWidget(self.status_label)
        self.setLayout(self.layout)

        # Threads
        self.sensor_thread = None
        self.logging_thread = None
        self.uart_thread = None

        # Button Connections
        self.start_button.clicked.connect(self.start_threads)
        self.stop_button.clicked.connect(self.stop_threads)

    def start_threads(self):
        """Start the sensor, logging, and UART threads."""
        global terminate_program
        terminate_program = False

        # Start sensor averaging thread
        if not self.sensor_thread or not self.sensor_thread.is_alive():
            self.sensor_thread = threading.Thread(target=sensor_check, daemon=True)
            self.sensor_thread.start()

        # Start data logging thread
        if not self.logging_thread or not self.logging_thread.is_alive():
            self.logging_thread = threading.Thread(target=data_log, daemon=True)
            self.logging_thread.start()

        # Start UART communication thread
        if not self.uart_thread or not self.uart_thread.is_alive():
            self.uart_thread = threading.Thread(target=uart_thread, daemon=True)
            self.uart_thread.start()

        self.status_label.setText("Status: Running")
        self.start_button.setDisabled(True)
        self.stop_button.setEnabled(True)
        logger.info("Threads started.")

    def stop_threads(self):
        """Stop all threads."""
        global terminate_program
        terminate_program = True

        if self.sensor_thread and self.sensor_thread.is_alive():
            self.sensor_thread.join()

        if self.logging_thread and self.logging_thread.is_alive():
            self.logging_thread.join()

        if self.uart_thread and self.uart_thread.is_alive():
            self.uart_thread.join()

        self.status_label.setText("Status: Stopped")
        self.start_button.setEnabled(True)
        self.stop_button.setDisabled(True)
        logger.info("Threads stopped.")

    def closeEvent(self, event):
        """Handle window close event."""
        self.stop_threads()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThreadController()
    window.show()
    sys.exit(app.exec_())
