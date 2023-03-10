# logitech-f710-evdev-interface

virtual_device.py connects to the controller via the linux event subsystem ('/dev/input/eventX'). By default, all of the controller inputs are mapped incorrectly, so the goal of virtual_device.py is to create a virtual game device that mimics the original one, but remap all of the values so it's easier to read and parse the inputs. virtual_device_read.py reads the values in from the virtual device and does all the parsing. 

It is requried to first run virtual_device.py and then virtual_device_read.py
