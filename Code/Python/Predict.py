import cv2
import math

from ultralytics import YOLO  # Make sure this supports YOLOv11

from GPS import detection_coordinate

# CONSTANTS
IMAGE_WIDTH = 1920
IMAGE_HEIGHT = 1080

#SCALE_FACTOR = 14.8     # Parken test image
SCALE_FACTOR = 77      # Full HD (1920x1080) images from drone camera


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


# MAIN
#image_center_geo_pos = (55.702718, 12.572308)   # Centre spot in Parken
image_center_geo_pos2 = (55.6541372, 12.1439169)



# Heading of drone in degrees (0=Heading North, 90=Heading East, ...))
#image_heading = 43.5    # Heading of test image of Parken
image_heading = -6.6

# Coordinate of detected object in pixels
#detection_coordinate = (346, 539)       # Left penalty spot
#detection_coordinate = (1736, 38)      # Top right corner flag

#mob_geo_pos = calc_mob_pos(image_center_geo_pos2, image_heading, detection_coordinate)

#print(mob_geo_pos)


# Load YOLOv11 model
model = YOLO('best4.pt')  # Replace with the correct path/model name

# Load video file
video_path ='Validation_Video_1.mp4'
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error opening video file.")
    exit()

# Output video settings
output_path = 'output_yolov11.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(1920)
height = int(1080)
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

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

        #Setting up values for detection coordinate
        z1 = x1
        z2 = y1
        detection_coordinate = z1,z2
        d = str(detection_coordinate)
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




# Breddegrad (Latitude):
# Horisontale linjer der løber parallelt med Ækvator. Ækvator er 0 grader.
# Nord for Ækvator betegnes "Nord" og angives som positive tal,
# syd for Ækvator betegnes som "Syd" og angives med negative tal.
# Nordpolen er 90 grader Nord (90 grader), Sydpolen er 90 grader Syd (-90 grader),
# Roskilde er 55,6 grader Nord (55,6 grader).
#

# Længdegrad (Longitude):
# Vertikale linjer der løber fra Nordpolen til Sydpolen. 0 grader går gennem Greenwich-observatoriet.
# Vest for Greenwich betegnes "Vest" og angives som negative tal,
# øst for Greenwich betegnes som "Øst" og angives med positive tal.
# Roskilde er 12,08 grader Øst (12,08 grader).













