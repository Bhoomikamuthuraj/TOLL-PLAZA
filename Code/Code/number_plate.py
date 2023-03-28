import cv2
import pytesseract
from PIL import Image

#importing harcascade files
harcascade = "C:\Code\model\haarcascade_russian_plate_number.xml"
pytesseract.pytesseract.tesseract_cmd ='C:/Program Files/Tesseract-OCR/tesseract.exe'

#video capture by camera
cap=cv2.VideoCapture(0)

cap.set(3, 640)    #width
cap.set(3, 640)    #height

min_area = 600
count=1

while True:
    success, img = cap.read()

    plate_cascade = cv2.CascadeClassifier(harcascade)      #loading harcascade xml file
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)       #converting to gray scale image 

    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)       

    for (x,y,w,h) in plates:
        area = w * h

        if area > min_area:
            cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)

            img_roi = img[y: y+h, x:x+w]
            cv2.imshow("roi", img_roi)

            grayscale_img = cv2.cvtColor(img_roi,cv2.COLOR_BGR2GRAY)    #converting image to gray scales

            cv2.imwrite("C:/Code/plate_images/plates/scanned_img"+str(count)+".jpg", img_roi)

            result = pytesseract.image_to_string(img_roi)
            #cv2.putText(img, result, (x,y-5), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,255), 2)

    cv2.imshow('result',img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(result)
        break




