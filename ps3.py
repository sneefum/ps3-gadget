from typing import Iterator
import os
import math
from enum import Enum

if os.geteuid() != 0:
    raise PermissionError("This module must be ran as root!")

class Button(Enum):
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

    PS =       0x10000 # Special Case

    X =         Cross # Some people call it X instead of Cross, this is here to prevent naming issues

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Button({self.name})"

class Buttons:
    def __init__(self) -> None:
        self.pressed = 0x0000
        self.ps_button = False

    def __bytes__(self) -> bytes:
        return self.pressed.to_bytes(2, "big")

    def __iter__(self) -> Iterator[Button]:
        return iter([Button(1 << i) for i in range(16) if self.pressed & (1 << i) > 0])

    def __repr__(self) -> str:
        return f"Buttons({str(self.buttons_pressed())[1:-1]})"

    def buttons_pressed(self) -> list[str]:
        return [str(Button(1 << i)) for i in range(16) if self.pressed & (1 << i) > 0]

    def press_button(self, button: Button) -> None:
        if button == Button.PS:
            self.ps_button = True
        else:
            self.pressed |= button.value

    def release_button(self, button: Button) -> None:
        if button == Button.PS:
            self.ps_button = False
        else:
            self.pressed &= ~button.value & 0xFFFF

class Stick:
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y

    def __bytes__(self) -> bytes:
        return bytes([round((self.x + 1) * 127.5), round((self.y + 1) * 127.5)])

    def __iter__(self) -> Iterator[int]:
        return iter([round((self.x + 1) * 127.5), round((self.y + 1) * 127.5)])

    def __repr__(self) -> str:
        return f"Stick({self.x}, {self.y})"

    def tilt_stick(self, x: float, y: float) -> None:
        magnitude = max(1, ((x*x) + (y*y))**0.5)
        self.x = x / magnitude
        self.y = y / magnitude

    def tilt_stick_angle(self, angle: float, magnitude: float) -> None:
        self.tilt_stick(math.sin(angle) * magnitude, math.cos(angle) * magnitude)

class Controller:
    def __init__(self, dev: str = "/dev/hidg0") -> None:
        self.dev = dev

        self.buttons = Buttons()
        
        self.left_stick = Stick()
        self.right_stick = Stick()

        # TODO: Implement Accelerometer and Gyroscope
    
    def send_input(self) -> None:
        with open(self.dev, "wb") as hid:
            packet = self.generate_input_packet()
            hid.write(packet)

    def generate_input_packet(self) -> bytes:
        packet = [] # 49 byte packet

        packet.append(0x01) # Report ID (1 => Input Packet)
        packet.append(0x00) # Unknown
        packet.append(bytes(self.buttons)[0]) # Buttons High Byte
        packet.append(bytes(self.buttons)[1]) # Buttons Low Byte
        packet.append(int(self.buttons.ps_button)) # Playstation Button
        packet.append(0x00) # Unknown
        packet.extend(list(self.left_stick)) # Left Stick
        packet.extend(list(self.right_stick)) # Right Stick
        packet.extend([0x00] * 2) # Unknown
        packet.append(0x00) # TODO: Something called move_power_status
        packet.append(0x00) # Unknown
        packet.extend([
            255 * (self.buttons.pressed & Button.Up.value > 0),
            255 * (self.buttons.pressed & Button.Right.value > 0),
            255 * (self.buttons.pressed & Button.Down.value > 0),
            255 * (self.buttons.pressed & Button.Left.value > 0),
            255 * (self.buttons.pressed & Button.L2.value > 0),
            255 * (self.buttons.pressed & Button.R2.value > 0),
            255 * (self.buttons.pressed & Button.L1.value > 0),
            255 * (self.buttons.pressed & Button.R1.value > 0),
            255 * (self.buttons.pressed & Button.Triangle.value > 0),
            255 * (self.buttons.pressed & Button.Circle.value > 0),
            255 * (self.buttons.pressed & Button.Cross.value > 0),
            255 * (self.buttons.pressed & Button.Square.value > 0)
        ]) # Order of these buttons is different from the actual pressed buttons, so I have to do it manually.
        packet.extend([0x00] * 3) # Unknown
        packet.extend([0x02, 0xEE, 0x10]) # Controller Status: Plugged In, Charging, Wired with Rumble Enabled
        packet.extend([0x00] * 9) # Resered
        packet.extend([0x01, 0xFF] * 4) # TODO: Accel and Gyro
       
        if len(packet) > 49:
            raise ValueError(f"Packet is too long! Expected 49 bytes and got {len(packet)}!")
        if len(packet) < 49:
            raise ValueError(f"Packet is too short! Expected 49 bytes and got {len(packet)}!")

        packet_bytes = bytes(packet)

