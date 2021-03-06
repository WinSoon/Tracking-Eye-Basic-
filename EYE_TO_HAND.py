from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import gpiozero
import RPi.GPIO as GPIO

camera = PiCamera()
image_width = 640
image_height = 480
camera.resolution = (image_width, image_height)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(image_width, image_height))
center_image_x = image_width / 2
center_image_y = image_height / 2
minimum_area = 250
maximum_area = 100000
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)
GPIO.setup(25,GPIO.OUT)



lower_color = np.array([35,74,6])
upper_color = np.array([64, 255, 255])

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	image = frame.array

	hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

	color_mask = cv2.inRange(hsv, lower_color, upper_color)

	contours, hierarchy = cv2.findContours(color_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

	object_area = 0
	object_x = 0
	object_y = 0

	for contour in contours:
		x, y, width, height = cv2.boundingRect(contour)
		found_area = width * height
		center_x = x + (width / 2)
		center_y = y + (height / 2)
		if object_area < found_area:
			object_area = found_area
			object_x = center_x
			object_y = center_y
	if object_area > 0:
		ball_location = [object_area, object_x, object_y]
	else:
		ball_location = None

	if ball_location:
		if (ball_location[0] > minimum_area) and (ball_location[0] < maximum_area):
			if ball_location[1] > (center_image_x + (image_width/3)):
				print("OBJECT GOING TO LEFT, ROBOT GO RIGHT")
				GPIO.output(18,GPIO.HIGH)
				GPIO.output(23,GPIO.HIGH)
				GPIO.output(24,GPIO.HIGH)
				GPIO.output(25,GPIO.LOW)

			elif ball_location[1] < (center_image_x - (image_width/3)):
				print("OBJECT GOING TO RIGHT, ROBOT GO LEFT")
				GPIO.output(18,GPIO.HIGH)
				GPIO.output(23,GPIO.HIGH)
				GPIO.output(24,GPIO.LOW)
				GPIO.output(25,GPIO.HIGH)
			
			elif ball_location[2] < (center_image_y - (image_height/3)):
				print("OBJECT GOING UP, ROBOT GO UP")
				GPIO.output(18,GPIO.LOW)
				GPIO.output(23,GPIO.HIGH)
				GPIO.output(24,GPIO.HIGH)
				GPIO.output(25,GPIO.HIGH)
				
			elif ball_location[2] > (center_image_y + (image_height/3)):
				print("OBJECT GOING DOWN, ROBOT GO DOWN")
				GPIO.output(18,GPIO.HIGH)
				GPIO.output(23,GPIO.LOW)
				GPIO.output(24,GPIO.HIGH)
				GPIO.output(25,GPIO.HIGH)
			else:
				print("Centre")
				GPIO.output(18,GPIO.HIGH)
				GPIO.output(23,GPIO.HIGH)
				GPIO.output(24,GPIO.HIGH)
				GPIO.output(25,GPIO.HIGH)
				
		elif (ball_location[0] < minimum_area):
			print("Target isn't large enough, searching")
		else:
			print("Target large enough, stopping")
	else:
		print("Target not found, searching")
	cv2.imshow("Frames",image)
	cv2.imshow("Mask",color_mask)
	rawCapture.truncate(0)
	
	key=cv2.waitKey(1)
	if key == 27:
	 break
