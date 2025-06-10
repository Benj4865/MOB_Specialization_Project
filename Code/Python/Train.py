## Code take from: https://docs.ultralytics.com/models/yolo11/#usage-examples and modified
from ultralytics import YOLO

# Load a pretrained YOLOv11 model. We chose the nano version
model = YOLO("yolo11n.pt")

# Setting up training parameters for the training
results = model.train(data= "path to yaml.", epochs=100, imgsz=640, workers = 16, device = 0, patience = 0)
