#-----Step 1: Use VideoCapture in OpenCV-----
import cv2
import dlib
import math
import numpy as np
import time
import pyautogui as gui
from tqdm import tqdm

BLINK_RATIO_THRESHOLD = 5.7

blink='Eye Blinking Not Detected !!!'

#-----Step 5: Getting to know blink ratio

def midpoint(point1 ,point2):
	return (point1.x + point2.x)/2,(point1.y + point2.y)/2

def euclidean_distance(point1 , point2):
	return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def get_blink_ratio(eye_points, facial_landmarks):
	
	#loading all the required points
	corner_left  = (facial_landmarks.part(eye_points[0]).x, 
					facial_landmarks.part(eye_points[0]).y)
	corner_right = (facial_landmarks.part(eye_points[3]).x, 
					facial_landmarks.part(eye_points[3]).y)
	
	center_top    = midpoint(facial_landmarks.part(eye_points[1]), 
							 facial_landmarks.part(eye_points[2]))
	center_bottom = midpoint(facial_landmarks.part(eye_points[5]), 
							 facial_landmarks.part(eye_points[4]))

	#calculating distance
	horizontal_length = euclidean_distance(corner_left,corner_right)
	vertical_length = euclidean_distance(center_top,center_bottom)

	ratio = horizontal_length / vertical_length

	return ratio


#-----Step 3: Face detection with dlib-----
detector = dlib.get_frontal_face_detector()

#-----Step 4: Detecting Eyes using landmarks in dlib-----
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
#these landmarks are based on the image above 
left_eye_landmarks  = [36, 37, 38, 39, 40, 41]
right_eye_landmarks = [42, 43, 44, 45, 46, 47]
