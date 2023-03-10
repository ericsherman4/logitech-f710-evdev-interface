import evdev
import atexit
import sys
from time import sleep
from evdev import categorize, ecodes

# plan
# define an update rate
# for 1/update rate seconds, read inputs
# sift through all the inputs and store it a struct that holds the state for everyting

# OR
# always update the struct as fast as possible but then only send the contents at update rate.
# should do this ebcause idk if there is a way to "flush" i.e on flushing if the user to constanly providing
# input, it will never stop

class g:
    update_rate = 10 # in hz
    time_to_read = 1 / update_rate
    joy_name = "Logitech Logitech Cordless RumblePad 2"
    test_input = False

# handle args
if len(sys.argv) > 1: 
    first_arg = sys.argv[1].lower()
    if first_arg == "true":
        g.test_input = True
        print("In testing input mode, code will not create a virtual device.")
    
if not g.test_input:
    print("In normal operation mode, code will create a virtual device.")
sleep(1)


dev = None
found = False
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)
    if(device.name == g.joy_name):
        dev = device
        found = True
        print("Found correct controller.")

if not found:
    print("unable to find joystick. exiting...")
    exit()

print("---------------")

print("printing device capabilities")
for item in dev.capabilities(verbose=True).items():
    print("")
    print(item) 

print("---------------")

atexit.register(dev.ungrab) #bind the function so its called at program exit
dev.grab() # grab the device so no other program can use it.
            # also prevents keyboard from omitting original events?

# this relies on the following files
# /usr/include/linux/input.h
# /usr/include/linux/input-event-codes.h

# have a remap dict for keys
# non-keys are handled in the loop because its mapping abs events to key events
# in inputs.h the #defines have a hex value associated with them
# can only use #defines with values that show up in the device capabilities FOR THE VIRTUAL DEVICE
REMAP_DICT_KEYS = {
    # A B X Y
    ecodes.BTN_C : ecodes.BTN_B,
    ecodes.BTN_X : ecodes.BTN_Y,
    ecodes.BTN_NORTH : ecodes.BTN_Y,
    ecodes.BTN_A : ecodes.BTN_X,
    ecodes.BTN_GAMEPAD : ecodes.BTN_X,
    ecodes.BTN_SOUTH: ecodes.BTN_X,
    ecodes.BTN_B : ecodes.BTN_A,
    ecodes.BTN_EAST : ecodes.BTN_A,

    # L/R joystick press
    # L joy pres -> BTN_C
    # R joy pres -> BTN_Z
    # why? see notes above dict.
    ecodes.BTN_SELECT : ecodes.BTN_C,
    ecodes.BTN_START : ecodes.BTN_Z,


    # back, start buttons
    # back button -> select button
    # why? see notes above dict.
    ecodes.BTN_TL2 : ecodes.BTN_SELECT,
    ecodes.BTN_TR2 : ecodes.BTN_START,



    # RB, RT, LT, LB
    # RB -> TR
    # LB -> TL
    # RT -> TR2
    # LT -> TL2
    ecodes.BTN_Z : ecodes.BTN_TR,
    ecodes.BTN_TR : ecodes.BTN_TR2,
    ecodes.BTN_TL : ecodes.BTN_TL2,
    ecodes.BTN_WEST : ecodes.BTN_TL,
    ecodes.BTN_Y : ecodes.BTN_TL,
}

# EVENT.TYPE = EV_ABS
## L and R joystick remain the same
# LY joystick is ABS_Y
# LX joystick is ABS_X
# RY joystick is ABS_RZ
# RX joystick is ABS_Z
## DPAD
# DPAD_UP/DOWN original is ABS_HAT0Y
# DPAD_LEFT/RIGHT original is ABS_HAT0X


if g.test_input:
    for event in dev.read_loop():

        # all buttons (including the joystick switch) besides mode, vibration, and D pad.
        # and logitech button which idk what that does.
        if event.type == ecodes.EV_KEY:
            print(categorize(event))

        # mode looks like it switches D -pad with Left joystick in terms of the values that it reads.
        # but on these event is dpad rjoy and ljoy
        if event.type == ecodes.EV_ABS:
            # print(categorize(event))
            print(event)


        # none of the buttons are on here
        if event.type == ecodes.EV_REL:
            print(categorize(event))

else:
    with evdev.UInput.from_device(dev, name="devremap") as ui:
        for event in dev.read_loop():

            if event.type == ecodes.EV_KEY:
                if event.code in REMAP_DICT_KEYS:
                    remapped_code = REMAP_DICT_KEYS[event.code]
                    ui.write(ecodes.EV_KEY, remapped_code, event.value)
                else:
                    ui.write(ecodes.EV_KEY, event.code, event.value)

            # elif event.type == ecodes.EV_ABS:
            #     if event.code == ecodes.ABS_HAT0Y:
            #         if event.value == -1:
            #             print("entered")
            #             ui.write(ecodes.EV_KEY, ecodes.BTN_DPAD_UP, 1)
            # doesnt work because DPAD stuff is not within device capabilties. Which is fine IG. 

            else:
                ui.write(event.type, event.code, event.value)

    
    