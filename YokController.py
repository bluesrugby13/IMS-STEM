#import evdev
from evdev import InputDevice, categorize, ecodes
yokPad = InputDevice('/dev/input/event3')
print (yokPad)

for event in yokPad.read_loop():
	if event.type == ecodes.EV_KEY:
		print ("EV_KEY: " + str(event))
	elif event.type == ecodes.EV_ABS:
		absevent = categorize(event)
		axis = ecodes.bytype[absevent.event.type][absevent.event.code]
		if axis == "ABS_X":
			if absevent.event.value == 1:
				print ("Release ABS_X - middle")
			elif absevent.event.value == 0:
				print ("Run to left")
			elif absevent.event.value == 2:
				print ("Run to the right")
		elif axis == "ABS_Y":
			if absevent.event.value == 1:
				print ("Release ABS_Y - middle")
			elif absevent.event.value == 0:
				print ("Run forward")
			elif absevent.event.value == 2:
				print ("Run backward")
