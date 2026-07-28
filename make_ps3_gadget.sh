#!/bin/bash

if [ "$EUID" -ne 0 ]; then
	exec sudo "$0" "$@"
fi

modprobe -r g_ether
modprobe libcomposite

cd /sys/kernel/config/usb_gadget
mkdir ps3_gamepad
cd ps3_gamepad

# pwd

echo 0x054C | tee idVendor # Sony
echo 0x0268 | tee idProduct # PS3 Controller

mkdir -p strings/0x409 # 0x409 is for English (USA)
cd strings/0x409

# pwd

echo "SNEEFUM676767" | tee serialnumber # I think I can put anything here without a problem
echo "Sony Corp." | tee manufacturer
echo "PlayStation 3 Controller" | tee product

cd ../..

# pwd

mkdir -p functions/hid.usb0
cd functions/hid.usb0

# pwd

echo 0 | tee protocol
echo 0 | tee subclass
echo 49 | tee report_length

cd ../..

# pwd

mkdir -p configs/c.1
ln -s functions/hid.usb0 configs/c.1/hid.usb0
ls /sys/class/udc | tee UDC
