import ps3

con = ps3.Controller()

print(con.left_stick)

con.left_stick.tilt_stick(1, 0)

print(con.left_stick)
