from typing import Iterator
import os

if os.geteuid() != 0:
    raise PermissionError("This module must be ran as root!")

class Button:
    L2 =       0x0001
    R2 =       0x0002
    L1 =       0x0004
    R1 =       0x0008
    Triangle = 0x0010
    Circle =   0x0020
    Cross =    0x0040
    Square =   0x0080
    Select =   0x0100
    L3 =       0x0200
    R3 =       0x0400
    Start =    0x0800
    Up =       0x1000
    Right =    0x2000
    Down =     0x4000
    Left =     0x8000

    X = Cross # Some people call it X instead of Cross, this is here to prevent naming issues

class Stick:
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y

    def __bytes__(self) -> bytes:
        return bytes([round(self.x + 1 * 127.5), round(self.y + 1 * 127.5)])

    def __iter__(self) -> Iterator[int]:
        return iter([round(self.x + 1 * 127.5), round(self.y + 1 * 127.5)])

    def __repr__(self) -> str:
        return f"Stick({self.x}, {self.y})"

    def tilt_stick(self, x, y) -> None:
        self.x = x
        self.y = y

class Controller:
    def __init__(self) -> None:
        self.buttons = []
        self.ps = False
        
        self.left_stick = Stick()
        self.right_stick = Stick()

        # TODO: Implement Accelerometer and Gyroscope
        # TODO: Proper handling of button pressure and analog L2 and R2
    
    def send_input(self, dev="/dev/hidg0") -> None:
        with open(dev, "wb") as hid:
            packet = self.generate_input_packet()
            hid.write(packet)

    def generate_input_packet(self) -> bytearray:
        packet = [] # 49 byte packet

        packet.append(0x01) # Report ID (1 => Input Packet)
        packet.append(0x00) # Unknown
        packet.append(self.buttons >> 8 % 255) # Buttons
        packet.append(self.buttons % 255) # Buttons
        packet.append(int(self.ps)) # Playstation Button
        packet.append(0x00) # Unknown
        packet.extend(list(self.left_stick)) # Left Stick
        packet.extend(list(self.right_stick)) # Right Stick
        packet.extend([0x00] * 2) # Unknown
        packet.append(0x00) # TODO: Something called move_power_status
        packet.append(0x00) # Unknown
        packet.extend([
            255 * self.buttons & Button.Up > 0,
            255 * self.buttons & Button.Right > 0,
            255 * self.buttons & Button.Down> 0,
            255 * self.buttons & Button.Left > 0,
            255 * self.buttons & Button.L2 > 0,
            255 * self.buttons & Button.R2 > 0
            255 * self.buttons & Button.L1 > 0,
            255 * self.buttons & Button.R1 > 0,
            255 * self.buttons & Button.Triangle > 0,
            255 * self.buttons & Button.Circle > 0,
            255 * self.buttons & Button.Cross > 0,
            255 * self.buttons & Button.Square> 0
        ]) # Order of these buttons is different from the actual pressed buttons, so I have to do it manually.
        packet.extend([0x00] * 3) # Unknown
        packet.extend([0x02, 0xEE, 0x10]) # Controller Status: Plugged In, Charging, Wired with Rumble Enabled
        packet.extend([0x00] * 9) # Resered
        packet.extend([0xFF, 0x01] * 4) # TODO: Accel and Gyro
       
        if len(packet) > 49:
            raise ValueError(f"Packet is too long! Expected 49 bytes and got {len(packet)}!")
        if len(packet) < 49:
            raise ValueError(f"Packet is too short! Expected 49 bytes and got {len(packet)}!")

        packet_bytes = bytearray(packet)

        return packet_bytes 
