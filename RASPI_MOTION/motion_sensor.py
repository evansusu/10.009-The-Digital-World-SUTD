import RPi.GPIO as GPIO
from time import sleep

from libdw import pyrebase

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
    rm_no = sd["rm_no"]
    sleep_time = float(sd["sleep_time"])
    gpio = int(sd["gpio"])
except:
    print("[ERROR] Invalid settings file. See README.txt for an example settings file.")
    print("[INFO] An error occurred and the program has stopped.")
    exit()

try:
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
except:
    print("[ERROR] Unable to connect to database.")
    print("[INFO] An error occurred and the program has stopped.")
    exit()

    
# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio, GPIO.IN)

while True:
    i = GPIO.input(gpio)
    if i == 0:
        print ('[INFO] No one detected.')

    elif i == 1:
        print ('[INFO] Motion detected.')
        try:
            db.child(rm_no + 'take_pic').set("True")
        except:
            print("[ERROR] Could not write to database.")
            print("[INFO] An error occurred and the program has stopped.")
            break
        sleep(sleep_time * 60)
        
