from ast import Try
from re import split
import cv2
import math
import serial

from ultralytics import YOLO

from GPS import detection_coordinate

# CONSTANTS
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080


SCALE_FACTOR = 77      # Full HD (1920x1080) images from drone camera


# Creating the Serial object used for the communication
ser = serial.Serial( 
    port='COM12',   # What port the Arduino is connected
    baudrate=9600,       # The speed at which the device communicate
    parity=serial.PARITY_NONE, 
    stopbits=serial.STOPBITS_ONE, 
    bytesize=serial.EIGHTBITS, 
    timeout=1
    )

# Standard way of reading data from a serial port
def read_Serial_data():
    try:
        up_data = ser.readline()
        split_data = up_data.split(",")

        heading = float(split_data[0])
        latitude = float(split_data[1])
        longitude = float(split_data[2])

        return (heading, latitude, longitude)

    except:
        print("Error reading data from serial")
        return None



def calc_mob_pos(image_center_geo_pos, image_heading, detection_coordinate):
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
    # This first alpha version does not do lens correction, but it is still pretty accurate (error is less than 50 cm)
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


# Load YOLOv11 model
model = YOLO('best4.pt')  # Replace with the correct path/model name

# Load video file
video_path ='Validation_Video_1.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error opening video file.")
    exit()

# Output video settings
width = int(1920)
height = int(1080)


frame = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference
    results = model(frame)[0]
    detectionID = 0


    # Draw detections
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = box.conf[0]
        cls = int(box.cls[0])
        label = f"{model.names[cls]} {conf:.2f}"

        #detection_coordinate = 0,0
        z1 = x1
        z2 = y1
        detection_coordinate = z1,z2
        d = str(detection_coordinate)
        print("Detection_Coordinate: " + d)
        
        # Getting newest data from serial
        (heading,latitude, longitude) = read_Serial_data()
        image_center_geo_pos = (latitude, longitude)

        # Calculating the position of the detection based on the image center position, heading and detection coordinate
        mob_geo_pos = calc_mob_pos(image_center_geo_pos, heading, detection_coordinate)

        s = str(mob_geo_pos)
        print(s)
        text = str(detectionID)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, text + ": " + label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        if detectionID == 0:
            cv2.putText(frame, text + " " + s,(100,100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        elif detectionID == 1:
            cv2.putText(frame, text + " " + s,(100,200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        detectionID += 1

    cv2.imshow("YOLOv11 Detection", frame)
    out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
