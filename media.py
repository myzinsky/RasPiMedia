#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import os
import Tkinter as tk
from array import *
from PIL import Image, ImageTk
from pygame import mixer
import subprocess

GPIO.setmode(GPIO.BCM)

# Pfade konfigurieren:
STICK  = "/media/pi/INTENSO/"
BILDER = STICK+"bilder/"
MUSIK  = STICK+"musik/"
VIDEOS = STICK+"videos/"

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

# Pause, Stop, Auswahl1, Auswahl2 :
T1 = 12 # Auswahl 1
T2 = 13 # Auswahl 2
T3 = 16 # Pause
T4 = 19 # Stopp 
GPIO.setup(T1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(T2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(T3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(T4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(T1, GPIO.BOTH, callback=lambda x: toggleLED1(),   bouncetime=300)
GPIO.add_event_detect(T2, GPIO.BOTH, callback=lambda x: toggleLED2(),   bouncetime=300)
GPIO.add_event_detect(T3, GPIO.BOTH, callback=lambda x: OnPausePress(), bouncetime=300)
GPIO.add_event_detect(T4, GPIO.BOTH, callback=lambda x: OnStoppPress(), bouncetime=300)

# Zustandsvariablen:
pause = False
state1 = False
state2 = False

# Videoplayer handle:
omxc = None

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
    global omxc
    if pause == False:
        pause = True
        mixer.music.pause()
        if omxc.poll() == None:
            omxc.stdin.write('p')
    else:
        pause = False
        mixer.music.unpause()
        if omxc.poll() == None:
            omxc.stdin.write('p')

def toggleLED1():
    global state1
    state1 = not state1
    GPIO.output(LED1, state1);

def toggleLED2():
    global state2
    state2 = not state2
    GPIO.output(LED2, state2);

def OnStoppPress():
    mixer.music.stop()
    os.system("killall omxplayer.bin")

def OnButtonPress(button): 
    global state1
    global omxc
    if state1 == False and state2 == False:	
        global panel
        global img
        f = BILDER+str(button)+".jpg"

        if os.path.exists(f):
            img = loadAndResizeImage(f)
        else:
            img = loadAndResizeImage(BILDER+"0.jpg")
        panel['image'] = img
        os.system("killall omxplayer.bin")
    elif state1 == True and state2 == False:
        f = MUSIK+str(button)+".mp3"
        print(f)

        if os.path.exists(f):
           os.system("killall omxplayer.bin")
           mixer.music.load(f)
           mixer.music.play() 
    elif state1 == False and state2 == True:
        # TODO
        print(" ")
    elif state1 == True and state2 == True:
        f = VIDEOS+str(button)+".mp4"
        print(f)
        if os.path.exists(f):
            os.system("killall omxplayer.bin")
            mixer.music.stop() 
            omxc = subprocess.Popen(['omxplayer', '-b', f], stdin=subprocess.PIPE)

def key(e):
    if e.char == "q":
        exit()

# Warte bis der STICK eingesteckt ist:
start = False
while start == False:
    # Ueberpruefe ob STICK eingesteckt ist:
    if os.path.exists(STICK) == True:
        start = True

# MP3 PLayer Initialisieren:
mixer.init()

# LEDs ausschalten:
GPIO.output(LED1, False);
GPIO.output(LED2, False);

# Fenster Anlegen:
window = tk.Tk()
window.attributes("-fullscreen", True)
window.bind("<KeyPress>", key)

img = loadAndResizeImage(BILDER+"0.jpg")

panel = tk.Label(window, image=img, bg="black")
panel.pack(side="bottom", fill="both", expand="yes")

window.mainloop()
