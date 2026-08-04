#!/bin/bash

if [ "$EUID" -ne 0 ]; then
	exec sudo "$0" "$@"
fi

modprobe -r g_ether
modprobe libcomposite

cd /sys/kernel/config/usb_gadget
mkdir ps3_gamepad
cd ps3_gamepad

echo 0x054C | tee idVendor # Sony
echo 0x0268 | tee idProduct # PS3 Controller

mkdir -p strings/0x409 # 0x409 is for English (USA)
cd strings/0x409

echo "24F133E966DB4D" | tee serialnumber # Any ASCII string should work as long as it's not too long.
echo "Sony Corp." | tee manufacturer
echo "PLAYSTATION(R)3 Controller" | tee product

cd ../..

mkdir -p functions/hid.usb0
cd functions/hid.usb0

echo 0 | tee protocol
echo 0 | tee subclass
echo 49 | tee report_length
echo 05010904A101A102850175089501150026FF00810375019513150025013500450105091901291381027501950D0600FF8103150026FF0005010901A10075089504350046FF0009300931093209358102C005017508952709018102750895300901B102C0A10285EE750895300901B102C0A10285EF750895300901B102C0C0 | xxd -r -ps | tee report_desc # RANDOM BULLSHIT GO!!!!

cd ../..

mkdir -p configs/c.1
ln -s functions/hid.usb0 configs/c.1/hid.usb0
ls /sys/class/udc | tee UDC
