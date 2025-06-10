## Importing pakages and setting up the environment for YOLOv11 object detection and the calculations
## Some of the generic setup and runinng of the YOLOv11 model is based on the Ultralytics YOLOv11 documentation at: https://docs.ultralytics.com/models/yolo11/#usage-examples
## Some of the Haversine implementation is inspired by: https://www.geeksforgeeks.org/haversine-formula-to-find-distance-between-two-points-on-a-sphere/
import cv2
import math
import serial
from ultralytics import YOLO


## CONSTANTS for the videoframe-size
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

## Calculated from the drone video 
## Described in report
SCALE_FACTOR = 77


# Setting up variables with None-values to enable a check if they are empty
latitude = None
longitude = None
heading = None


# Creating the Serial object used for the communication
ser = serial.Serial( 
    # What port the Arduino is connected to in windows, on linux this would be something like-
    # '/dev/ttyACM0' or '/dev/ttyUSB0
    port='COM12',   

    # The speed at which the device communicate
    baudrate=9600,       
    parity=serial.PARITY_NONE, 
    stopbits=serial.STOPBITS_ONE, 
    bytesize=serial.EIGHTBITS, 
    timeout=1
    )

# Standard way of reading data from a serial port
def read_Serial_data():
    return (123,55.123456,12.123456)
    try:
        up_data = ser.readline()
        #Convert form binary to string
        up_data = up_data.decode('ascii')

        split_data = up_data.split(",")

        heading = float(split_data[0])
        latitude = float(split_data[1])
        longitude = float(split_data[2])

        return (heading, latitude, longitude)

    except:
        print("Error reading data from serial")
        return None



def calc_pob_pos(image_center_geo_pos, image_heading, detection_coordinate):

    # Set up some local variables to make the code easier to read
    angle_rad = math.radians(image_heading) *-1
    detection_x, detection_y = detection_coordinate
    image_center_x = IMAGE_WIDTH / 2
    image_center_y = IMAGE_HEIGHT / 2

    # Rotation matrix multiplication to get rotated x & y
    relative_x = (detection_x - image_center_x) * math.cos(angle_rad) - (image_center_y - detection_y) * math.sin(angle_rad)
    relative_y = (detection_x - image_center_x) * math.sin(angle_rad) + (image_center_y - detection_y) * math.cos(angle_rad)
    true_detection_x = image_center_x + relative_x
    true_detection_y = image_center_y + relative_y

    # Calculate detected object's distance (meters) relative to center of image
    distance_east = (true_detection_x - image_center_x) / SCALE_FACTOR
    distance_north = (true_detection_y - image_center_y) / SCALE_FACTOR

    # Calculate real world position by offsetting image center position with distances calculated
    # R is earths radius in meters used for Haversine calculations
    R = 6378137

    # Offset in radians
    offset_north_rad = distance_north / R
    offset_east_rad = distance_east / (R * math.cos(math.pi * image_center_geo_pos[0] / 180))

    mob_latitude = image_center_geo_pos[0] + offset_north_rad * 180 / math.pi
    mob_longitude = image_center_geo_pos[1] + offset_east_rad * 180 / math.pi

    mob_geo_pos = (mob_latitude, mob_longitude)

    return mob_geo_pos


## Load YOLOv11 model
model = YOLO('best3.pt')

## Open Webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error opening video file.")
    exit()

## Continueing to run as long as the video capture is opened and accessible
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    ## Run inference using loaded model
    results = model(frame)[0]
    detectionID = 0

    # Getting newest data from serial connection
    serial_data = read_Serial_data()

    #Only update when heading, latitude and longitude are valid.
    if serial_data is not None:
        (heading, latitude, longitude) = serial_data
        image_center_geo_pos = (latitude, longitude)


    # Get detection-coordinates and make prediction for each detection in the frame
    for detection in results.boxes:
        x1, y1, x2, y2 = map(int, detection.xyxy[0])
        conf = detection.conf[0]
        cls = int(detection.cls[0])
        label = f"{model.names[cls]} {conf:.2f}"

        ## Setting up detection coordinate variables
        z1 = x1
        z2 = y1
        detection_coordinate = z1,z2
        d = str(detection_coordinate)
        print("Detection_Coordinate: " + d)

        ## If not invalid data is present in the serial data, then calculate the position of the detection
        if latitude is not None and longitude is not None and heading is not None:

            # Calculating the position of the detection based on the image center position, heading and detection coordinate
            pob_Geo_Pos = calc_pob_pos(image_center_geo_pos, heading, detection_coordinate)

    ## Setting up escape-key if the user wants to stop the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

## Releasing the video capture object and closing all OpenCV windows upon exit
cap.release()
cv2.destroyAllWindows()
