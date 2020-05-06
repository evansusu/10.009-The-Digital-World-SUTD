from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

import webbrowser

from libdw import pyrebase

from functools import partial

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


# initialise the firebase connection
try:
    config = {
        "apiKey": sd["apikey"],
        "databaseURL": sd["url"],
    }

    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
except:
    print("[ERROR] Unable to connect to database.")
    print("[INFO] An error occurred and the program has stopped.")
    exit()


kv = Builder.load_file("login_menu.kv")


class WindowManager(ScreenManager):
    pass

# set a default room number to prevent errors
roomNo = "55-0-0"
class LoginWindow(Screen):
    # checks whether the provided username and password are correct
    def check(self):
        f = open("registered.txt", "r").readlines() [1:]
        database = []
        for l in f:
            k,v = l.split()
            database.append((k,v))
        global roomNo
        roomNo = str(self.roomno.text)
        if (self.studentid.text, self.roomno.text) in database:
            self.reset()
            sm.current = 'terms'
        else:
            invalidLogin()
    
    def reset(self):
        self.studentid.text = ''
        self.roomno.text = ''

    def quit(self):
        App.get_running_app().stop()


def invalidLogin():
    pop = Popup (title='Invalid', content=Label(text= 'Wrong ID or Room Number'), size_hint = (None,None), size= (400,400) )
    pop.open()
    
class TermsWindow(Screen):
    pass

class MainWindow(Screen):

    # moves the user to the appropriate screen for his/her block
    def checkRms(self):
        global roomNo
        
        g = str(roomNo)
        block, floor, room = g.split("-")

        if block == '55':
            sm.current = 'Blk55'
        elif block == '57':
            sm.current = 'Blk57'
        elif block == '59':
            sm.current = 'Blk59'

    def external(instance):
        webbrowser.open('hms.sutd.edu.sg')

class HousingRules(Screen):
    pass


class Blk59(Screen):
    # reads the last recorded data from the database and displays it
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            b5904_p = db.child('5904no_of_people').child("ppl_cnt").get().val()
            b5904_t = db.child('5904no_of_people').child("last_time").get().val()

            b5906_p = db.child('5906no_of_people').child("ppl_cnt").get().val()
            b5906_t = db.child('5906no_of_people').child("last_time").get().val()

            b5910_p = db.child('5910no_of_people').child("ppl_cnt").get().val()
            b5910_t = db.child('5910no_of_people').child("last_time").get().val()
        except Exception as e:
            print("[ERROR] " + str(e))
            b5904_p = b5904_t = 0
            b5906_p = b5906_t = 0
            b5910_p = b5910_t = 0

        self.b5904.text = "Last detected {} people at {}.".format(b5904_p, b5904_t)
        self.b5906.text = "Last detected {} people at {}.".format(b5906_p, b5906_t)
        self.b5910.text = "Last detected {} people at {}.".format(b5910_p, b5910_t)

        self.rmDict = {}
        self.rmDict["5904"] = self.b5904
        self.rmDict["5906"] = self.b5906
        self.rmDict["5910"] = self.b5910

        self.eventDict = {}
        self.eventDict["5904"] = None
        self.eventDict["5906"] = None
        self.eventDict["5910"] = None

    # sends a request to the database to take a pic and perform the object recognition
    def checkRm(self, rm):
        try:
            db.child(rm + 'take_pic').set("True")
            self.rmDict[rm].text = "Request sent. Please wait."
            if self.eventDict[rm] is None:
                self.eventDict[rm] = Clock.schedule_interval(partial(self.updateText, rm), 5)
        except:
            print("[ERROR] Unable to connect to database.")
            self.rmDict[rm].text = "Unable to connect to database."
            return

    def check(self, rm = 'all'):
        if rm == 'all':
            self.checkRm('5904')
            self.checkRm('5906')
            self.checkRm('5910')
        else:
            self.checkRm(rm)

    # continuously checks the database for when analysing is done and updates text accordingly
    def updateText(self, rm, *largs):
        running = db.child(rm + 'take_pic').get().val()
        if running == "False":
            self.eventDict[rm].cancel()
            self.eventDict[rm] = None
            ppl_cnt = db.child(rm + 'no_of_people').child('ppl_cnt').get().val()
            last_time = db.child(rm + 'no_of_people').child('last_time').get().val()
            self.rmDict[rm].text = "Last detected {} people at {}.".format(ppl_cnt, last_time)

    # gets the latest data from the database and updates the text
    def refresh(self):
        try:
            b5904_p = db.child('5904no_of_people').child("ppl_cnt").get().val()
            b5904_t = db.child('5904no_of_people').child("last_time").get().val()

            b5906_p = db.child('5906no_of_people').child("ppl_cnt").get().val()
            b5906_t = db.child('5906no_of_people').child("last_time").get().val()

            b5910_p = db.child('5910no_of_people').child("ppl_cnt").get().val()
            b5910_t = db.child('5910no_of_people').child("last_time").get().val()
        except Exception as e:
            print("[ERROR] " + str(e))
            b5904_p = b5904_t = 0
            b5906_p = b5906_t = 0
            b5910_p = b5910_t = 0

        self.b5904.text = "Last detected {} people at {}.".format(b5904_p, b5904_t)
        self.b5906.text = "Last detected {} people at {}.".format(b5906_p, b5906_t)
        self.b5910.text = "Last detected {} people at {}.".format(b5910_p, b5910_t)



class Blk57(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            b5704 = db.child('5704no_of_people').child("ppl_cnt").get().val()
            b5704_t = db.child('5704no_of_people').child("last_time").get().val()

            b5706_p = db.child('5706no_of_people').child("ppl_cnt").get().val()
            b5706_t = db.child('5706no_of_people').child("last_time").get().val()

            b5710_p = db.child('5710no_of_people').child("ppl_cnt").get().val()
            b5710_t = db.child('5710no_of_people').child("last_time").get().val()
        except Exception as e:
            print("[ERROR] " + str(e))
            b5704 = b5704_t = 0
            b5706_p = b5706_t = 0
            b5710_p = b5710_t = 0

        self.b5704.text = "Last detected {} people at {}.".format(b5704, b5704_t)
        self.b5706.text = "Last detected {} people at {}.".format(b5706_p, b5706_t)
        self.b5710.text = "Last detected {} people at {}.".format(b5710_p, b5710_t)

        self.rmDict = {}
        self.rmDict["5704"] = self.b5704
        self.rmDict["5706"] = self.b5706
        self.rmDict["5710"] = self.b5710

        self.eventDict = {}
        self.eventDict["5704"] = None
        self.eventDict["5706"] = None
        self.eventDict["5710"] = None

    def checkRm(self, rm):
        try:
            db.child(rm + 'take_pic').set("True")
            self.rmDict[rm].text = "Request sent. Please wait."
            if self.eventDict[rm] is None:
                self.eventDict[rm] = Clock.schedule_interval(partial(self.updateText, rm), 5)
        except:
            print("[ERROR] Unable to connect to database.")
            self.rmDict[rm].text = "Unable to connect to database."
            return

    def check(self, rm = 'all'):
        if rm == 'all':
            self.checkRm('5704')
            self.checkRm('5706')
            self.checkRm('5710')
        else:
            self.checkRm(rm)

    def updateText(self, rm, *largs):
        running = db.child(rm + 'take_pic').get().val()
        if running == "False":
            self.eventDict[rm].cancel()
            self.eventDict[rm] = None
            ppl_cnt = db.child(rm + 'no_of_people').child('ppl_cnt').get().val()
            last_time = db.child(rm + 'no_of_people').child('last_time').get().val()
            self.rmDict[rm].text = "Last detected {} people at {}.".format(ppl_cnt, last_time)

    def refresh(self):
        try:
            b5704 = db.child('5704no_of_people').child("ppl_cnt").get().val()
            b5704_t = db.child('5704no_of_people').child("last_time").get().val()

            b5706_p = db.child('5706no_of_people').child("ppl_cnt").get().val()
            b5706_t = db.child('5706no_of_people').child("last_time").get().val()

            b5710_p = db.child('5710no_of_people').child("ppl_cnt").get().val()
            b5710_t = db.child('5710no_of_people').child("last_time").get().val()
        except Exception as e:
            print("[ERROR] " + str(e))
            b5704 = b5704_t = 0
            b5706_p = b5706_t = 0
            b5710_p = b5710_t = 0



class Blk55(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            b5504_p = db.child('5504no_of_people').child("ppl_cnt").get().val()
            b5504_t = db.child('5504no_of_people').child("last_time").get().val()

            b5506_p = db.child('5506no_of_people').child("ppl_cnt").get().val()
            b5506_t = db.child('5506no_of_people').child("last_time").get().val()

            b5510_p = db.child('5510no_of_people').child("ppl_cnt").get().val()
            b5510_t = db.child('5510no_of_people').child("last_time").get().val()
        except Exception as e:
            print("[ERROR] " + str(e))
            b5504_p = b5504_t = 0
            b5506_p = b5506_t = 0
            b5510_p = b5510_t = 0

        self.b5504.text = "Last detected {} people at {}.".format(b5504_p, b5504_t)
        self.b5506.text = "Last detected {} people at {}.".format(b5506_p, b5506_t)
        self.b5510.text = "Last detected {} people at {}.".format(b5510_p, b5510_t)

        self.rmDict = {}
        self.rmDict["5504"] = self.b5504
        self.rmDict["5506"] = self.b5506
        self.rmDict["5510"] = self.b5510

        self.eventDict = {}
        self.eventDict["5504"] = None
        self.eventDict["5506"] = None
        self.eventDict["5510"] = None

    def checkRm(self, rm):
        try:
            db.child(rm + 'take_pic').set("True")
            self.rmDict[rm].text = "Request sent. Please wait."
            if self.eventDict[rm] is None:
                self.eventDict[rm] = Clock.schedule_interval(partial(self.updateText, rm), 5)
        except:
            print("[ERROR] Unable to connect to database.")
            self.rmDict[rm].text = "Unable to connect to database."
            return

    def check(self, rm = 'all'):
        if rm == 'all':
            self.checkRm('5504')
            self.checkRm('5506')
            self.checkRm('5510')
        else:
            self.checkRm(rm)

    def updateText(self, rm, *largs):
        running = db.child(rm + 'take_pic').get().val()
        if running == "False":
            self.eventDict[rm].cancel()
            self.eventDict[rm] = None
            ppl_cnt = db.child(rm + 'no_of_people').child('ppl_cnt').get().val()
            last_time = db.child(rm + 'no_of_people').child('last_time').get().val()
            self.rmDict[rm].text = "Last detected {} people at {}.".format(ppl_cnt, last_time)

    def refresh(self):
        try:
            b5504_p = db.child('5504no_of_people').child("ppl_cnt").get().val()
            b5504_t = db.child('5504no_of_people').child("last_time").get().val()

            b5506_p = db.child('5506no_of_people').child("ppl_cnt").get().val()
            b5506_t = db.child('5506no_of_people').child("last_time").get().val()

            b5510_p = db.child('5510no_of_people').child("ppl_cnt").get().val()
            b5510_t = db.child('5510no_of_people').child("last_time").get().val()
        except Exception as e:
            print("[ERROR] " + str(e))
            b5504_p = b5504_t = 0
            b5506_p = b5506_t = 0
            b5510_p = b5510_t = 0

        self.b5504.text = "Last detected {} people at {}.".format(b5504_p, b5504_t)
        self.b5506.text = "Last detected {} people at {}.".format(b5506_p, b5506_t)
        self.b5510.text = "Last detected {} people at {}.".format(b5510_p, b5510_t)


sm = WindowManager()

screens = [LoginWindow(name = 'login'), TermsWindow(name='terms'), MainWindow(name = 'main'), HousingRules(name = 'rules'), Blk59 (name = 'Blk59'), Blk57(name = 'Blk57'), Blk55(name = 'Blk55')]
for screen in screens:
    sm.add_widget(screen)

sm.current = 'login'

class GotSPACE(App):
    def build(self):
        return sm


if __name__ == "__main__":
    app = GotSPACE()
    app.run()