RASPBERRY PI CAMERA SETUP
1) Place the folder RASPI_CAM into a Raspberry Pi
2) Ensure that the Pi is connected to a camera
3) Install the required packages using "pip install -r camera_req.txt"
4) Edit settings.txt. More information as provided:
	url should be a valid firebase url
	apikey should be the api key for the aforementioned firebase
	base_dir is where the image recognition weights are stored (default is same directory as camera.py)
	min_confidence is a float between 0 and 1 (default 0.5)
	min_threshold is a float between 0 and 1 (default 0.3)
	rotation is the rotation adjustment for the Raspberry Pi camera
	rm_no is the room number is <block><floor> format
	debug is True if you want to save analysed images for debugging purposes (default False)
5) Run the python file using "python3 camera.py"

RASPBERRY PI MOTION SENSOR SETUP
1) Place the folder RASPI_MOTION into a Raspberry Pi
2) Ensure that the Pi is connected to a motion sensor.
3) Install the required packages using "pip install -r motion_req.txt"
4) Edit settings.txt. More information as provided:
	url should be a valid firebase url
	apikey should be the api key for the aforementioned firebase
	rm_no is the room number is <block><floor> format
	sleep_time is the time in minutes it will wait after detecting motion before it will start detecting motion again (default 30)
	gpio is the GPIO pin on the Pi that the motion sensor is connected to (default 19)
5) Run the python file using "python3 motion_sensor.py

GUI SETUP
1) Open the GUI folder
2) Install the required packages using "pip install -r gui_req.txt"
3) Edit settings.txt. More information as provided:
	url should be a valid firebase url
	apikey should be the api key for the aforementioned firebase
4) Run the python file using "python3 main.py"

Note: The GUI may take a while to start as it is getting data from the firebase. If the GUI crashes while opening, check that you have a valid internet connection.