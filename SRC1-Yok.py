#!/usr/bin/python
#Working SRC 2017 Code for 4 Servo Control
#2 Drive wheels, 1 Gripper and 1 Arm
#Revised 11.29.16 - Kevin Pace

# 5/21/19
# Added controller code for Yok Sony Playstation. Need to install python-dev
# in order to build the evdev libraries to capture events.

import sys
import os
import threading
from Adafruit_PWM_Servo_Driver import PWM
import time
try: #try to import the gpio libraries (need to download) and throw an exception if there is an error
	import RPi.GPIO as gpio
except RuntimeError:
	print "error importing the gpio library which is probably because you need to run this program with sudo"

# ===========================================================================
# evdev libraries for capturing Yok controller events. To install, need to
# first update python-dev do this by:
#               "sudo apt-get install python-dev"
# Then, install evdev by:
#               "sudo pip -install evdev"
# Good thing to also do an update for the OS:
#               "sudo apt-get update && sudo apt-get upgrade -Y
# When installing, an error may occur that requires removal of a file
#               "sudo rm -rf /var/lib/chksshpwd"
from evdev import InputDevice, categorize, ecodes

# Need to query and determine controller input. In the below call to InputDevice
# the yok controller for this machine is '/dev/input/event3'
yokPad = InputDevice('/dev/input/event3')

# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the PWM device using the default address
pwm = PWM(0x40)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x40, debug=True)

servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096
servoZero = (servoMax-servoMin)/2 + servoMin

servoLeft = 0
servoRight = 1
servoLift = 2
servoGrip = 3
servoClaw = 4

#gpio setup here
#outPin = 38
inPin = 40 #assign the gpio pins to variables
inPin2 = 38
#define inPin3 here below
""" inPin3 = """
gpio.setmode(gpio.BOARD)

#gpio.setup(outPin, gpio.OUT, initial=gpio.HIGH) #set the output pin to a permanent high, this will go directly into the input pin once the button is pressed
gpio.setup(inPin, gpio.IN) #setup pin 21 as input
gpio.setup(inPin2, gpio.IN)
#uncomment below to set the inPin3 to GPIO input
""" gpio.setup(inPin3, gpio.IN) """

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)

# Simple Servo Calls
def ServoClockwise(channel):
	pwm.setPWM(channel, 0, servoMin)

def ServoCounterClockwise(channel):
	pwm.setPWM(channel, 0, servoMax)

def ServoStop(channel):
	pwm.setPWM(channel, 0, servoZero)


#for the turn left and turn right functions, edit the sleep values for back up and turn to get the servo timing correct
def turnLeft():
	#print "right button pressed!"
	#back up
	ServoClockwise(servoLeft)
	ServoCounterClockwise(servoRight)
	time.sleep(1.2) #edit this
	#turn left
	#print "second part of left turn"
	ServoClockwise(servoLeft)
	ServoClockwise(servoRight)
	time.sleep(0.8) #edit this

def turnRight():
    #print "left button pressed"
    #back up
    ServoClockwise(servoLeft)
    ServoCounterClockwise(servoRight)
    time.sleep(1.2) #edit this
    #turn right
    ServoCounterClockwise(servoLeft)
    ServoCounterClockwise(servoRight)
    time.sleep(0.8) # edit this

"""  Here is the heart of the autonomous mode! """

def autoMode():
    print "got here"
    while True:
        ServoCounterClockwise(servoLeft)
        ServoClockwise(servoRight)
        print gpio.input(inPin), "  ", gpio.input(inPin2)
        if gpio.input(inPin) == 1: #if the button is pressed, back off the wall and turn left
                print "break button pressed"
                break
        elif gpio.input(inPin2) == 1: #where inPin2 should be the button on the left side of the robot
                turnRight() #function I defined above

        #uncomment below but make sure to define inPin3 as whichever GPIO pin you intend to have the right switch hooked up to
        """ elif gpio.input(inPin3) == 1
            turnleft() """


# ULTRASONIC MODE
"""
1) stop at a certain distance measured by the sensor from the maze wall
2) pause
3) look left, pause, then measure the distance and store that distance in a temporary variable
4) look right, pause, measure the dist and store in a temp variable
5) look straight
6) compare the temporary variables and if the rightDistance > leftDistance, turn right.  If leftDistance >= rightDistance, turn left.
7) execute the turn and continue movement in that direction.
8) repeat or loop these steps until user breaks out of the autonomous loop
"""


# Keyboard stuff

import Tkinter as tk

global toggle
toggle = True

def yok_event_loop():
	for event in yokPad.read_loop():
                if event.type == ecodes.EV_KEY:
                        print ("EV_KEY (TODO): " + str(event))
		elif event.type == ecodes.EV_ABS:
                	absevent = categorize(event)
                        axis = ecodes.bytype[absevent.event.type][absevent.event.code]
                        if axis == "ABS_X":
                                if absevent.event.value == 1:
                                        #print ("Release ABS_X - middle")
                                        process_release_yok()
                                elif absevent.event.value == 0:
					#print ("Run to left")
					left_turn_yok()
				elif absevent.event.value == 2:
                                        #print ("Run to the right")
                                        right_turn_yok()
                        elif axis == "ABS_Y":
                                if absevent.event.value == 1:
                                        #print ("Release ABS_Y - middle")
                                        process_release_yok()
                                elif absevent.event.value == 0:
                                        #print ("Run forward")
                                        forward_yok()
                                elif absevent.event.value == 2:
                                        #print ("Run backward")
                                        backward_yok()
def process_release_yok():
        print ("Releasing yok.....")
        ServoStop(servoLeft)
        ServoStop(servoRight)
        ServoStop(servoLift)
        ServoStop(servoGrip)
        ServoStop(servoClaw)
        
def right_turn_yok():
        print ("right turn yok")
        ServoCounterClockwise(servoLeft)
        ServoCounterClockwise(servoRight)
        
def left_turn_yok():
        print ("left turn yok")
        ServoClockwise(servoLeft)
        ServoClockwise(servoRight)
        
def forward_yok():
        print ("forward yok")
        ServoCounterClockwise(servoLeft)
        ServoClockwise(servoRight)
        
def backward_yok():
        print ("backward yok")
        ServoClockwise(servoLeft)
        ServoCounterClockwise(servoRight)
        
class MyFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        # method call counter
        self.pack()
        self.afterId = None
	
        root.bind('<KeyPress>', self.key_press)
        root.bind('<KeyRelease>', self.key_release)
        root.bind('<F11>', self.toggle_fullscreen)
        root.bind('<Escape>', self.end_fullscreen)
       	root.attributes('-fullscreen', True)
        yok_event_loop()

		
            
    def toggle_fullscreen(self, event=None):
        global toggle
        toggle = not toggle
        root.attributes('-fullscreen', toggle)
        return "break"

    def end_fullscreen(self, event=None):
        root.attributes('-fullscreen', False)
        print 'end fullscreen'
        global toggle
        toggle = False
        return "break"

    def key_press(self, event):
        if self.afterId != None:
            self.after_cancel( self.afterId )
            self.afterId = None
        else:
            #print 'key pressed %s' % event.char
            if event.char == "w":
                #text.insert('end', ' FORWARD ')
                ServoCounterClockwise(servoLeft)
                ServoClockwise(servoRight)
            elif event.char == "d":
                #text.insert('end', ' RIGHT_TURN ')
                ServoCounterClockwise(servoLeft)
                ServoCounterClockwise(servoRight)
            elif event.char == "k":
                #text.insert('end', ' Quit ')
                pwm.setPWM(0, 0, servoZero)
                root.destroy()
            elif event.char == "s":
                #text.insert('end', ' BACKWARD ')
                ServoClockwise(servoLeft)
                ServoCounterClockwise(servoRight)
            elif event.char == "a":
                #text.insert('end', ' LEFT_TURN ')
                ServoClockwise(servoLeft)
                ServoClockwise(servoRight)
            elif event.char == "[":
                #text.insert('end', ' UP ')
                ServoClockwise(servoLift)
            elif event.char == "]":
                #text.insert('end', ' DOWN ')
                ServoCounterClockwise(servoLift)
            elif event.char == "-":
                #text.insert('end', ' CLOSE_GRIP ')
                ServoClockwise(servoGrip)
            elif event.char == "=":
                #text.insert('end', ' OPEN_GRIP ')
                ServoCounterClockwise(servoGrip)
            #elif event.char == "l":
                #text.insert('end', ' Stop Auto Mode ')
                #autoMode() #refer to the defined function above
            elif event.char == "S":
                os.system('sudo shutdown now -h')
            elif event.char == "R":
                os.system('sudo shutdown -r now /r')
            elif event.char == "0":
                ServoClockwise(servoClaw)
            elif event.char == "9":
                ServoCounterClockwise(servoClaw)

    def key_release(self, event):
        self.afterId = self.after_idle( self.process_release, event )

    def process_release(self, event):
        ServoStop(servoLeft)
        ServoStop(servoRight)
        ServoStop(servoLift)
        ServoStop(servoGrip)
        ServoStop(servoClaw)
	#print 'key release %s' % event.char
        self.afterId = None



# Program
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz


root = tk.Tk()
root.geometry('800x600')
root.attributes('-fullscreen', False)
text = tk.Text(root, background='black', foreground='white', font=('Comic Sans MS', 12))
text.pack()
text.insert('end', 'STEM TRI-Fecta 2017')
app1 = MyFrame(root)
root.mainloop()

print("done")

