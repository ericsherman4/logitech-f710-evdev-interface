import evdev
from evdev import InputDevice, categorize, ecodes

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)


dev_path = ""
# get the event number
if len(devices) == 1:
    dev_path = devices[0].path
else:
    print("more than one device found, exiting")
    exit()

print("verifying..")
device = evdev.InputDevice(dev_path)
print(device)

print(device.capabilities())
print("adad")

# for each in ecodes:
#     print(each)


# print(device.leds(verbose=True))

for event in device.read_loop():

    # all buttons (including the joystick switch) besides mode, vibration, and D pad.
    # and logitech button which idk what that does.
    if event.type == ecodes.EV_KEY:
        print(categorize(event))

    # mode looks like it switches D -pad with Left joystick in terms of the values that it reads.
    # but on these event is dpad rjoy and ljoy
    if event.type == ecodes.EV_ABS:
        print(categorize(event))


    # none of the buttons are on here
    if event.type == ecodes.EV_REL:
        print(categorize(event))
