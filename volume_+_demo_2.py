### volume.py imports
import os
import alsaaudio
from RPi import GPIO
from time import sleep
import snowboydecoder
import sys
import signal

os.system('clear') #clear screen, this is just for the OCD purposes
 
#setup mixer module
m = alsaaudio.Mixer(control='Speaker',cardindex =2)

#Constants and variables
MAX_VOLUME = 100 #set the maximum volume
DIRECTION  = -1   #set the direction to increase volume 1 or -1
STEP = 5 #linear steps for increasing/decreasing volume
amplifying = False #amplifying state
volume = int(m.getvolume()[0])  #volume of the speakers
clkLastState = GPIO.input(clk)  #Laststate of the clk pin 
dtLastState = GPIO.input(dt)    #Laststate of the dt pin 
swLastState = GPIO.input(sw)    #Laststate of the sw pin
 
#tell to GPIO library to use logical PIN names/numbers, instead of the physical PIN numbers
GPIO.setmode(GPIO.BCM) 
 
#set up the pins we are been using
clk = 17
dt = 18
sw = 27
red = 23
green = 22
blue = 24



#set up the GPIO events on those pins
GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 
#get the initial states


### demo.py variables
interrupted = False

"""
if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    #sys.exit(-1)

model = sys.argv[1]
"""
model = "/home/pi/Desktop/project/hello.pmdl"
    

###volume.py definitions
#define functions which will be triggered on pin state changes
def clkClicked(channel):
    global volume
    global STEP
    global amplifying

    clkState = GPIO.input(clk)
    dtState = GPIO.input(dt)
    if amplifying == False:
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
    if amplifying == False: 
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
        m.setvolume(int(volume))
    else:
        amplifying = True
        m.setvolume(0)
    
    print ("amplifying ", amplifying)             
                 
print ("Initial clk:", clkLastState)
print ("Initial dt:", dtLastState)
print ("Initial sw:", swLastState)
print ("Initial volume:", volume)
print ("=========================================")

### demo.py definitions
def signal_handler(signal, frame):
    global interrupted
    interrupted = True
 
def interrupt_callback():
    global interrupted
    return interrupted

def led_light():
    GPIO.output(green,GPIO.HIGH)
    sleep(1)
    GPIO.output(green,GPIO.LOW)
    sleep(1)
    GPIO.output(red,GPIO.HIGH)
    sleep(1)
    GPIO.output(red,GPIO.LOW)
    sleep(1)
    GPIO.output(blue,GPIO.HIGH)
    sleep(1)
    GPIO.output(blue,GPIO.LOW)

#capture SIGINT signal, e.g., Ctrl + C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5,audio_gain=3)


### volume.py eventhandlers

#set up the interrupts
GPIO.add_event_detect(clk, GPIO.FALLING, callback=clkClicked, bouncetime=50)
GPIO.add_event_detect(dt, GPIO.FALLING, callback=dtClicked, bouncetime=50)
GPIO.add_event_detect(sw, GPIO.FALLING, callback=swClicked, bouncetime=300)
print('Listening... Press Ctrl + C to exit')
### demo.py
#main loop
detector.start(detected_callback=led_light,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)


### demo.py terminator
detector.terminate()
### volume.py terminator
GPIO.cleanup()


