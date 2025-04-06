from ultralytics import YOLO
import cv2

# Load the model
model = YOLO("diabetic.pt")

# Run inference
results = model(["image23.jpg"])

# Process results and save without labels
for result in results:
    img = result.plot(labels=False)  # Draw results without labels
    cv2.imwrite("result2.jpg", img)  # Save the output image