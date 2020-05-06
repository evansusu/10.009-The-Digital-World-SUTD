'''Put this file in the same directory as yolo-coco folder'''

import numpy as np
import argparse
import time
import cv2
import os

from picamera import PiCamera

from libdw import pyrebase

# load settings file
try:
	with open('settings.txt') as f:
		s = f.readlines()
except:
	print("[ERROR] Settings file not found.")
	print("[INFO] An error occurred and the program has stopped.")
	exit()

# intialise a settings dictionary
sd = {}
for l in s:
	if l.rstrip() != '':
		k,v = l.rstrip().split(',')
		sd[k] = v

try:
	config = {
		"apiKey": sd["apikey"],
		"databaseURL": sd["url"],
	}

	# image recognition variables
	base_dir = sd["base_dir"]
	min_confidence = float(sd["min_confidence"])
	min_threshold = float(sd["min_threshold"])

	# setup variables
	rotation = float(sd["rotation"])
	rm_no = sd["rm_no"]
	debug_img = sd["debug"] == "True"
except:
	print("[ERROR] Invalid settings file. See README.txt for an example settings file.")
	print("[INFO] An error occurred and the program has stopped.")
	exit()

# load database
try:
	firebase = pyrebase.initialize_app(config)
	db = firebase.database()
except:
	print("[ERROR] Unable to connect to database.")
	print("[INFO] An error occurred and the program has stopped.")
	exit()


# find the necessary YOLO files
try:
	labelsPath = os.path.sep.join([base_dir, "coco.names"])
	LABELS = open(labelsPath).read().strip().split("\n")

	np.random.seed(1356)
	COLOURS = np.random.randint(0, 255, size = (len(LABELS), 3), dtype = "uint8")

	weightsPath = os.path.sep.join([base_dir, "yolov3.weights"])
	configPath = os.path.sep.join([base_dir, "yolov3.cfg"])

	print("[INFO] loading YOLO from disk")
	net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
except:
	print("[Error] Unable to find the required files.")
	print("[INFO] An error occurred and the program has stopped.")
	exit()

# initialise the raspi camera
camera = PiCamera()
camera.rotation = rotation

# let the camera warm-up
time.sleep(0.1)

while True:

	# wait for a response from the database
	try:
		take_pic = db.child(rm_no + 'take_pic').get().val() == "True"
	except:
		print("[ERROR] Unable to connect to database.")
		break

	if not take_pic:
		print("[INFO] Waiting for a request.")

	try:
		while not take_pic:
			time.sleep(10)
			take_pic = db.child(rm_no + 'take_pic').get().val() == "True"
	except:
		print("[ERROR] Unable to connect to database.")
		break

	if take_pic:
		print("[INFO] Performing person detection.")
		take_pic = False

	# take a picture
	camera.capture("./temp.jpg")
	image = cv2.imread("./temp.jpg")
	(H, W) = image.shape[:2]

	# delete the picture
	os.remove("./temp.jpg")

	# perform YOLO object detection
	ln = net.getLayerNames()
	ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

	blob = cv2.dnn.blobFromImage(image, 1 / 255, (416, 416), swapRB = True, crop = False)
	net.setInput(blob)
	start = time.time()
	layerOutputs = net.forward(ln)
	end = time.time()

	print("[INFO] YOLO took {:.6f} seconds.".format(end - start))

	# analyse the results
	boxes = []
	confidences = []
	classIDs = []

	# construct the tracking geometries
	for output in layerOutputs:
		for detection in output:
			scores = detection[5:]
			classID = np.argmax(scores)
			confidence = scores[classID]

			if confidence > min_confidence:
				box = detection[0:4] * np.array([W, H, W, H])
				(centreX, centreY, width, height) = box.astype("int")

				x = int(centreX - (width / 2))
				y = int(centreY - (height / 2))

				boxes.append([x, y, int(width), int(height)])
				confidences.append(float(confidence))
				classIDs.append(classID)

	idxs = cv2.dnn.NMSBoxes(boxes, confidences, min_confidence, min_threshold)

	people_cnt = 0

	# analyse the results of YOLO object detection
	if len(idxs) > 0:
		for i in idxs.flatten():
			if LABELS[classIDs[i]] == "person":
				# count how many people are in the image
				people_cnt += 1

				# highlight the people for debugging purposes
				(x, y) = (boxes[i][0], boxes[i][1])
				(w, h) = (boxes[i][2], boxes[i][3])

				colour = [int(c) for c in COLOURS[classIDs[i]]]
				cv2.rectangle(image, (x, y), (x + w, y + h), colour, 2)
				text = "{}:{:.4f}".format(LABELS[classIDs[i]], confidences[i])
				cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 2)

	# print debug messages
	print("[INFO] People detected: {}".format(people_cnt))

	# catch network errors while writing to the database
	try:
		db.child(rm_no + "ppl_cnt").child("ppl_cnt_{}".format(time.strftime("%d/%m/%Y %H:%M"))).set(people_cnt)
		db.child(rm_no + "no_of_people").child("ppl_cnt").set(people_cnt)
		db.child(rm_no + "no_of_people").child("last_time").set(time.strftime("%d/%m/%Y %H:%M"))
		db.child(rm_no + 'take_pic').set("False")
	except:
		print("[ERROR] Could not write to database.")
		break

	# save the image for debugging purposes
	if debug_img:
		cv2.imwrite("./debug/debug_image_{}_{}.jpg".format(rm_no, time.strftime("%d_%m_%Y_%H%M")), image)

print("[INFO] An error occurred and the program has stopped.")