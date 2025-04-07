# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""CircuitPython status NeoPixel rainbow example."""
import time
import board
import neopixel


pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.01

def red():
    pixel.fill((255, 0, 0))

def yellow():
    pixel.fill((255, 255, 0))

def green():
    pixel.fill((0, 255, 0))

def delay(wanted_delay):
    start = time.time()
    end = time.time()
    while wanted_delay > end - start:
        end = time.time()

state = 0

while True:
    if state == 0:
        red()
        delay(3)
        state = 1
        ##print("Hello1")

    elif state == 1 or state == 3:
        yellow()
        delay(3)
        if state == 1:
            state = 2
        else:
            state = 0
            ##print("hello2")

    elif state == 2:
        green()
        delay(3)
        state = 3
        ##print("Hello3")
