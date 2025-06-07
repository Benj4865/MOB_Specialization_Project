## Importing pakages and setting up the environment for YOLOv11 object detection and the calculations
## Some of the generic setup and runinng of the YOLOv11 model is based on the Ultralytics YOLOv11 documentation at: https://docs.ultralytics.com/models/yolo11/#usage-examples
import cv2
import math
from ultralytics import YOLO 


## CONSTANTS for the videoframe-size
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

## Calculated from the drone video 
## Described in report
SCALE_FACTOR = 77

## Function for calculating the position of a detected object in the real world
def calc_mob_pos(image_center_geo_pos, image_heading, detection_coordinate):

    ## Set up some local variables to make the code easier to read
    angle_rad = math.radians(image_heading) *-1
    detection_x, detection_y = detection_coordinate
    image_center_x = IMAGE_WIDTH / 2
    image_center_y = IMAGE_HEIGHT / 2

    ## Rotation matrix multiplication to get image coordinates "rotated on x & y"
    relative_x = (detection_x - image_center_x) * math.cos(angle_rad) - (image_center_y - detection_y) * math.sin(angle_rad)
    relative_y = (detection_x - image_center_x) * math.sin(angle_rad) + (image_center_y - detection_y) * math.cos(angle_rad)
    true_detection_x = image_center_x + relative_x
    true_detection_y = image_center_y + relative_y

    ## Calculate detected object's distance (meters) relative to center of image
    distance_east = (true_detection_x - image_center_x) / SCALE_FACTOR
    distance_north = (true_detection_y - image_center_y) / SCALE_FACTOR

    ## Calculate real world position by offsetting image center position with distances calculated
    ## R is earths radius in meters used for Haversine calculations
    R = 6378137

    ## Offset in radians
    offset_north_rad = distance_north / R
    offset_east_rad = distance_east / (R * math.cos(math.pi * image_center_geo_pos[0] / 180))

    ## Calculate the new latitude and longitude based on the offsets
    mob_latitude = image_center_geo_pos[0] + offset_north_rad * 180 / math.pi
    mob_longitude = image_center_geo_pos[1] + offset_east_rad * 180 / math.pi

    ## Saving the results in a tuple
    mob_geo_pos = (mob_latitude, mob_longitude)

    ## Return the calculated position of the detected person
    return mob_geo_pos


## Manually inputting the center position of the image in geo-coordinates
image_center_geo_pos2 = (55.6541372, 12.1439169)

##  Manually inputting heading of drone in degrees (0=Heading North, 90=Heading East, ...))
image_heading = 3


## Load the pretrained YOLOv11 model
model = YOLO('best.pt')

## Load video file from disk for prediction
video_path ='Validation_Video_1.mp4'
## Open the video file
cap = cv2.VideoCapture(video_path)

## Check if the video opened successfully
if not cap.isOpened():
    print("Error opening video file.")
    exit()

## Setting up the output settings for the debug video
output_path = 'output_yolov11.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = cap.get(cv2.CAP_PROP_FPS)
width = IMAGE_WIDTH
height = IMAGE_HEIGHT
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

## Keeping a counter of the amount of frames
frame = 0

## Looping through the videos frames from the beginning
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference using the model
    results = model(frame)[0]

    ## Setting up detectionID to keep track of the number of people detected
    detectionID = 0


    # Draw detections
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = box.conf[0]
        cls = int(box.cls[0])
        label = f"{model.names[cls]} {conf:.2f}"

        ## Setting up the detection coordinate
        z1 = x1
        z2 = y1
        detection_coordinate = z1,z2
        d = str(detection_coordinate)
        ## Print the detection coordinate for debugging
        print("Detection_Coordinate: " + d)

        mob_geo_pos = calc_mob_pos(image_center_geo_pos2, 0.0, detection_coordinate)

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