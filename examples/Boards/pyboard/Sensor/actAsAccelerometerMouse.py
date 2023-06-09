#hardware platform: pyboard V1.1
# use this demo you should do:
# 1. open boot.py
# 2. enable pyb.usb_mode('VCP+HID')
# 3. close uPyCraft and reconnet pyboard for PC
# 4. open uPyCraft and run this demo
# 5. ctrl+c or stop could stop this demo
# Restoring your pyboard to normal
# 1. Hold down the USR switch.
# 2. While still holding down USR, press and release the RST switch.
# 3. The LEDs will then cycle green to orange to green+orange and back again.
# 4. Keep holding down USR until only the orange LED is lit, and then let go of the USR switch.
# 5. The orange LED should flash quickly 4 times, and then turn off.
# 6. You are now in safe mode.
import pyb
switch=pyb.Switch()
accel=pyb.Accel()                       #Accel is an object that controls the accelerometer
hid=pyb.USB_HID()                       #create USB_HID object.it can be used to emulate a peripheral such as a mouse or keyboard.
while not switch():
  hid.send((0,accel.x(),accel.y(),0))   #Send data over the USB HID interface