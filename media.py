#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import os
import Tkinter as tk
from array import *
from PIL import Image, ImageTk
from pygame import mixer

GPIO.setmode(GPIO.BCM)

# Pfade konfigurieren:
STICK  = "/media/pi/INTENSO/"
BILDER = STICK+"bilder/"
MUSIK  = STICK+"musik/"

# LEDs konfigurieren:
LED1 = 21 # Rot
LED2 = 20 # Gruen
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.output(LED1, False);
GPIO.output(LED2, False);

# Die 10 Taster Konfigurieren
T = [4,17,18,27,22,23,24,25,5,6]
for i in range(0,10):
    GPIO.setup(T[i], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(T[i], GPIO.BOTH, callback=lambda _, x=i: OnButtonPress(x+1), bouncetime=300)

# Schalter Konfigurieren:
S1 = 12
GPIO.setup(S1, GPIO.IN)
GPIO.add_event_detect(S1, GPIO.BOTH, callback=lambda x: toggleLED(), bouncetime=50)

# Pause und Stop:
T1 = 16 # Pause
T2 = 13 # Stopp
GPIO.setup(T1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(T2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(T1, GPIO.BOTH, callback=lambda x: OnPausePress(), bouncetime=300)
GPIO.add_event_detect(T2, GPIO.BOTH, callback=lambda x: OnStoppPress(), bouncetime=300)

# Pausenzustand:
pause = False

def loadAndResizeImage(f):
    global window
    width  = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    size = width, height
    p = Image.open(f)
    p.thumbnail(size, Image.ANTIALIAS)
    return ImageTk.PhotoImage(p)

def OnPausePress():
    global pause
    if pause == False:
        pause = True
        mixer.music.pause()
    else:
        pause = False
        mixer.music.unpause()

def toggleLED():
        GPIO.output(LED1, GPIO.input(S1));

def OnStoppPress():
    mixer.music.stop()

def OnButtonPress(button): 
    if GPIO.input(S1) == True:
        f = MUSIK+str(button)+".mp3"
        print(f)

        if os.path.exists(f):
           mixer.music.load(f)
           mixer.music.play() 
    else:	
        global panel
        global img
        f = BILDER+str(button)+".jpg"

        if os.path.exists(f):
            img = loadAndResizeImage(f)
        else:
            img = loadAndResizeImage(BILDER+"0.jpg")

        panel['image'] = img

def key(e):
    if e.char == "q":
        exit()

def checkStick():
    if os.path.exists(STICK):
        GPIO.output(LED2, True);
        return True
    else:
        GPIO.output(LED2, False);
        return False

# Warte bis der STICK eingesteckt ist:
start = False
while start == False:
    # Ueberpruefe ob STICK eingesteckt ist:
    if checkStick() == True:
        start = True

# MP3 PLayer Initialisieren:
mixer.init()

# LED nach Schalterstellung Konfigurieren:
GPIO.output(LED1, GPIO.input(S1));

# Fenster Anlegen:
window = tk.Tk()
window.attributes("-fullscreen", True)
window.bind("<KeyPress>", key)

img = loadAndResizeImage(BILDER+"0.jpg")

panel = tk.Label(window, image=img, bg="black")
panel.pack(side="bottom", fill="both", expand="yes")

window.mainloop()
