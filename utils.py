import face_recognition
import cv2
import time

from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
from datetime import datetime,timedelta
import imutils
import time
import cv2
import os
from blinks import *
process_this_frame = True

def faceRecognition():
	global process_this_frame
	global blink
	i=0
	f_image = []
	known_face_names = []
	known_face_encodings = []

	face_locations = []
	face_encodings = []
	face_names = []                  #to create a list of faces that match in the existing dataset
	known_locker = []

	for filename in os.listdir("dataset"):
		known_face_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file("dataset/"+filename))[0])
		known_face_names.append(filename.split('.')[0])
		known_locker.append(filename.split('.')[1])
		i = i + 1

	frame = cv2.imread('static/images/test_image.jpg')
	print(known_face_names)


	small_frame = cv2.resize(frame, (0, 0), fx=1, fy=1)
	cv2.imwrite('static/images/test_image1.jpg',small_frame)
	
	rgb_small_frame = small_frame[:, :, ::-1]
	
	face_locations = face_recognition.face_locations(rgb_small_frame)
	face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

	face_names = []
	lockers = []
	for face_encoding in face_encodings:
		
		matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
		name = "Unknown"

	
		if True in matches:
			first_match_index = matches.index(True)
			name = known_face_names[first_match_index]
			lockerID = known_locker[first_match_index]

		face_names.append(name)
		lockers.append(lockerID)
		

	process_this_frame = not process_this_frame
	return face_names,blink,people,lockers

def video_feed():
	global blink
	global people                            # faces detected by HAAR Cascade
	blink = 'Eye Blinking Not Detected !!!'
	# loop over the frames from the video stream
	# initialize the video stream and allow the camera sensor to warm up
	print("[INFO] starting video stream...")
	vs = cv2.VideoCapture(0)
	#vs = VideoStream(usePiCamera=True).start()
	time.sleep(2.0)

	faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

	while True:
		# grab the frame from the threaded video stream and resize it to
		# have a maximum width of 400 pixels
		ret,frame = vs.read()
		frame = imutils.resize(frame, width=400)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = faceCascade.detectMultiScale(
			gray,
	
			scaleFactor=1.2,
			minNeighbors=5
			,     
	   		minSize=(20, 20)
		)
		people = len(faces)
		for (x, y, w, h) in faces:
			cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
			face = frame[y:y + h, x:x + w]
			cv2.imwrite('static/images/test_image.jpg',face)

		faces,_,_ = detector.run(image = gray, upsample_num_times = 0, 
				adjust_threshold = 0.0)
		for face in faces:
			landmarks = predictor(gray, face)

			#-----Step 5: Calculating blink ratio for one eye-----
			left_eye_ratio  = get_blink_ratio(left_eye_landmarks, landmarks)
			right_eye_ratio = get_blink_ratio(right_eye_landmarks, landmarks)
			blink_ratio     = (left_eye_ratio + right_eye_ratio) / 2

			if blink_ratio > BLINK_RATIO_THRESHOLD:
				blink='Eye Blinking Detected..!!'

		cv2.putText(frame,blink,(10,50), cv2.FONT_HERSHEY_SIMPLEX,
					0.7,(255,0,10),1,cv2.LINE_AA)	

		imgencode=cv2.imencode('.jpg',frame)[1]
		stringData=imgencode.tostring()
		
		yield (b'--frame\r\n'
			b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

		key = cv2.waitKey(1) & 0xFF
	
		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break

	# close the output CSV file do a bit of cleanup
	print("[INFO] cleaning up...")
	csv.close()
	cv2.destroyAllWindows()
	vs.stop()

def isReady(last_login):                   #to check if 24 hours have passed
	now = datetime.now()
	date_time_obj = datetime.strptime(last_login, "%d/%m/%y,%H:%M:%S")
	if now-timedelta(hours=24) <= date_time_obj <=now:
		return False
	else:
		return True