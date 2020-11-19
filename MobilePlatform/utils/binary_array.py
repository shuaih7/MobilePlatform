import os, sys

title = b"\x03"
onDelay = b"\x04"
offDelay = b"\x0A"
brightness = b"\x41"

title = bytearray(title)
title.append(4)
title.append(11)
title.append(65)
print(bytearray([4,6,9,25]))