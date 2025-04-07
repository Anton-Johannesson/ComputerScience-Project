# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""CircuitPython status NeoPixel rainbow example."""
import time
import board
import neopixel
import digitalio
import pwmio

button = digitalio.DigitalInOut(board.D9)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

red_light = digitalio.DigitalInOut(board.D13)
yellow_light = digitalio.DigitalInOut(board.D12)
green_light = digitalio.DigitalInOut(board.D11)

red_light.direction = digitalio.Direction.OUTPUT
yellow_light.direction = digitalio.Direction.OUTPUT
green_light.direction = digitalio.Direction.OUTPUT

state = 0
button_pressed = False

def red_on():
    red_light.value = True

def yellow_on():
    yellow_light.value = True

def green_on():
    green_light.value = True

def red_off():
    red_light.value = False

def yellow_off():
    yellow_light.value = False

def green_off():
    green_light.value = False

def delay(delay_time):
    global button_pressed
    start = time.monotonic()
    end = time.monotonic()
    while delay_time > time.monotonic() - start:
        if not button.value == True:
            button_pressed = True

def sound():
    for i in range(10):
        pwm = pwmio.PWMOut(board.D10, duty_cycle = 2 ** 10, frequency = 660)
        delay(0.5)
        pwm.deinit()
        delay(0.5)

while True:
    if state == 0:
        red_on()
        if button_pressed:
            sound()
            button_pressed = False
        delay(1)
        red_off()
        state = 1

    elif state == 1:
        yellow_on()
        delay(3)
        yellow_off()
        state = 2

    elif state == 2:
        green_on()
        delay(3)
        green_off()
        state = 3

    elif state == 3:
        yellow_on()
        delay(3)
        yellow_off()
        state = 0