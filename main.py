import ps3

con = ps3.Controller()

con.left_stick.tilt_stick(1, 3) 
# x: 1, y: 3. normalizes to length 1
# (1, 3) -> (1/root 10, 3/root 10) ~= (0.316, 0.949)

con.right_stick.tilt_stick(0.1, 0)
# x: 0.1, y: 0. length < 1, no need to normalize.

con.buttons.press_button(ps3.Button.Select)
con.buttons.press_button(ps3.Button.Square) # Press the square button (obviously)
con.buttons.press_button(ps3.Button.PS) # PlayStation button, has special behavior


packet = con.generate_input_packet()

packet_readable = ""

count = 0
for byte in packet:
    if count % 7 == 0 and count != 0:
        packet_readable += "\n"
    packet_readable += f"{byte:02X} "
    count += 1

print(packet_readable) # Print the bytes that get sent over USB as an input
