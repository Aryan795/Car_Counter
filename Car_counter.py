import numpy as np
from PIL.ImageOps import scale
from cvzone import cornerRect
from torch.cuda import device
from ultralytics import YOLO
import  cv2
import cvzone
import math
from sort import *

cap=cv2.VideoCapture('../Videos/cars_1.mp4')

model=YOLO("../Yolo_Weights/yolov8l.pt")
classNames=['Person','bicycle','car','motorbike','aeroplane','bus','train','truck','boat','traffic light','fire hydrant','stop sign','parking meter','bench','bird','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack','umbrella','handbag','tie','suitcase','frisbee','skies','snowboard','sports ball','kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket','bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple','sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair','sofa','pottedplant','bed','diningtable','toilet','tvmoniter','laptop','mouse','remote','keyboard','cell phone','microwave','oven','toaster','sink','refrigerator','book','clock','vase','scissors','teddy bear','hair drier','toothbrush']

mask = cv2.imread("mask_new.png")

#Tracking
tracker=Sort(max_age=20,min_hits=3,iou_threshold=0.3)
limits = [225 , 283 , 530 , 285]
totalCount=[]


while True:
    success,img=cap.read()
    imgRegion = cv2.bitwise_and(img,mask)
    results=model(imgRegion,stream=True,device="mps")
    imgGraphics = cv2.imread("graphics.png",cv2.IMREAD_UNCHANGED)
    cvzone.overlayPNG(img,imgGraphics,(0,0))
    detections = np.empty((0,5))

    for r in results:
        boxes=r.boxes
        for box in boxes:

            # Bounding Box
            x1,y1,x2,y2=box.xyxy[0]
            x1, y1, x2, y2= int(x1),int(y1),int(x2),int(y2)
            w , h = x2-x1,y2-y1
            # cvzone.cornerRect(img,(x1,y1,w,h),l=9)

            # Confidence
            conf= math.ceil((box.conf[0]*100))/100
            # Class Name
            cls= int(box.cls[0])
            currentClass = classNames[cls]
            if currentClass in ["car", "bus", "truck", "motorbike"] and conf > 0.3:                # cvzone.cornerRect(img, (x1, y1, w, h), l=9,rt=5)
                # cvzone.putTextRect(img,f'{classNames[cls]} {conf}',(max(0,x1),max(35,y1)),scale=0.6,thickness=1,offset=2)
                currentArray = np.array([x1,y1,x2,y2,conf])
                detections = np.vstack((detections,currentArray))


    resultsTracker = tracker.update(detections)
    cv2.line(img,(limits[0],limits[1]),(limits[2],limits[3]),(0,0,255),5)
    for result in resultsTracker:
        x1,y1,x2,y2, Id=result
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        print(result)
        w, h = x2 - x1, y2 - y1
        cvzone.cornerRect(img,(x1,y1, w, h),l=9,rt=2, colorR=(255,0,255))
        cx,cy=x1+w//2,y1+h//2
        cv2.circle(img,(cx,cy),5,(255,0,255),cv2.FILLED)

        if limits[0]<cx<limits[2] and limits[1]-10<cy<limits[1]+10 :
            if totalCount.count(Id)==0:
                totalCount.append(Id)
                cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), 5)
    # cvzone.putTextRect(img,f'Count {len(totalCount)}',(50,50) )
    cv2.putText(img,str(len(totalCount)),(255,100),cv2.FONT_HERSHEY_PLAIN,5,(50,50,255),8)
    cv2.imshow("Image",img)
    # cv2.imshow("ImageRegion", imgRegion)
    cv2.waitKey(1)