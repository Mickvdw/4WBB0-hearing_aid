### volume.py imports
import os
import alsaaudio
from RPi import GPIO
import time
import snowboydetect
import snowboydecoder
import sys
import signal


#os.system('clear') #clear screen, this is just for the OCD purposes

#setup mixer module
m = alsaaudio.Mixer(control='Speaker',cardindex =3)

#capture SIGINT signal, e.g., Ctrl + C

#Constants and variables
TURN_OFF_TIME = 11000
MAX_VOLUME = 100                            #set the maximum volume
DIRECTION  = -1                             #set the direction to increase volume 1 or -1
STEP = 5                                    #linear steps for increasing/decreasing volume
amplifying = False                          #amplifying state
interrupted = False                         #intterrupted variable
prev_sound = int(round(time.time() * 1000)) #get the current time
prev_time = int(round(time.time() * 1000))  #get current time

#tell to GPIO library to use logical PIN names/numbers, instead of the physical PIN numbers
GPIO.setmode(GPIO.BCM)

#set up the pins we are using
clk = 17
dt = 18
sw = 27
red = 24
green = 22
blue = 23

#set up the GPIO events on those pins
GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.output(red, GPIO.LOW)
GPIO.output(green, GPIO.LOW)
GPIO.output(blue, GPIO.HIGH)
time.sleep(1)

#get initial values
volume = 50                     #volume of the speakers
clkLastState = GPIO.input(clk)  #Laststate of the clk pin
dtLastState = GPIO.input(dt)    #Laststate of the dt pin
swLastState = GPIO.input(sw)    #Laststate of the sw pin
m.setvolume(0)


### demo.py definitions
def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

signal.signal(signal.SIGINT, signal_handler)


#load the model en setup the detector for snowboy
model = "/home/pi/Desktop/project/hello.pmdl"
detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5,audio_gain=3)

###volume.py definitions
#define functions which will be triggered on pin state changes
def clkClicked(channel):
    global volume
    global STEP
    global amplifying

    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)
    if amplifying == True:
        if clkState == 0 and dtState == 1:
            volume = volume + (STEP * DIRECTION)
            if volume > MAX_VOLUME:
                volume = MAX_VOLUME
            elif volume < 0:
                volume = 0
        m.setvolume(int(volume))

    print ("Volume ", volume)

def dtClicked(channel):
    global volume
    global STEP
    global amplifying


    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)
    if amplifying == True:
        if clkState == 1 and dtState == 0:
            volume = volume - (STEP * DIRECTION)
            if volume > MAX_VOLUME:
                volume = MAX_VOLUME
            elif volume < 0:
                volume = 0
        m.setvolume(int(volume))

    print ("Volume ", volume)

def swClicked(channel):
    global amplifying
    global volume

    if amplifying:
        amplifying = False
        m.setvolume(0)
        led_light(red)
    else:
        amplifying = True
        m.setvolume(volume)
        led_light(green)

    print ("amplifying ", amplifying)

def led_light(color):
    if color == green:
        GPIO.output(green,GPIO.HIGH)
        GPIO.output(blue,GPIO.LOW)
        GPIO.output(red,GPIO.LOW)
    elif color == blue:
        GPIO.output(blue,GPIO.HIGH)
        GPIO.output(red,GPIO.LOW)
        GPIO.output(green,GPIO.LOW)
    elif color == red:
        GPIO.output(red,GPIO.HIGH)
        GPIO.output(green,GPIO.LOW)
        GPIO.output(blue,GPIO.LOW)

def turn_on():
    global volume
    global amplifying
    global prev_sound
    m.setvolume(int(volume))
    amplifying = True
    led_light(green)

def turn_off():
    global amplifying
    m.setvolume(0)
    amplifying = False
    led_light(red)

#set up the interrupts
GPIO.add_event_detect(clk, GPIO.FALLING, callback=clkClicked, bouncetime=50)
GPIO.add_event_detect(dt, GPIO.FALLING, callback=dtClicked, bouncetime=50)
GPIO.add_event_detect(sw, GPIO.FALLING, callback=swClicked, bouncetime=300)

print ("Initial clk:", clkLastState)
print ("Initial dt:", dtLastState)
print ("Initial sw:", swLastState)
print ("Initial volume:", volume)
print ("=========================================")
print('Listening... Press Ctrl + C to exit')

detector.start(detected_callback=turn_on, stop_amplifying=turn_off,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

### terminators
detector.terminate()
GPIO.cleanup()
