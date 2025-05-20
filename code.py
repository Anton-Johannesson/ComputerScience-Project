import time
import board
import digitalio
import pwmio
import busio
import adafruit_ahtx0
import adafruit_sgp30
import adafruit_ht16k33
from adafruit_ht16k33 import segments
import asyncio
import neopixel

# limits for values [CO2, TVOC, temp, humidity]
LIMITS = [1000, 300, 32, 70]

# Colors for limits
COLORS = [(10, 0, 0), (0, 10, 0)]

# initialize button
button = digitalio.DigitalInOut(board.D9)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.DOWN

#initialize neopixel
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

# initalize I2C bus for stemma
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
i2c.try_lock()

# start values
value_state = 0
state = 0
button_pressed = False
alarm = False

def start_pixel():
    global value_state
    global pixels
    
    # white for CO2
    if value_state == 0:
        pixels[0] = (10, 10, 10)
        
    # green for TVOC
    elif value_state == 1:
        pixels[0] = (0, 10, 0)
        
    # red for temperature
    elif value_state == 2:
        pixels[0] = (10, 0, 0)
        
    # blue for humidity
    else:
        pixels[0] = (0, 0, 10)
    return

# 
def stop_pixel():
    global pixels
    pixels[0] = (0, 0, 0)
    return

# 
def stop_alarm():
    global buzzer
    buzzer.duty_cycle = 0
    return
        
# 
def start_alarm():
    global buzzer
    buzzer.duty_cycle = 2 ** 10
    return

# 
def delay(delay_time):
    global button_pressed
    start = time.monotonic()
    while delay_time > time.monotonic() - start:
        if button.value:
            button_pressed = True
    return        
            
#
def delay_alarm():
    global button_pressed
    global pixels
    global alarm
    start_pixel()
    while not button_pressed:
        delay(1)
        print(button.value)
        if button_pressed:
            stop_alarm()
            
    stop_pixel()
    button_pressed = False
    alarm = False
    return

# Check to see if all modules are connected to the microcontroller
def start():
    if i2c.probe(0x38) == False:
        print("AHT20 sensor not found")
    elif i2c.probe(0x58) == False:
        print("SGP30 sensor not found")
    elif i2c.probe(0x70) == False:
        print("LED not found")
        
    print("Found sensors:")
    print(i2c.scan())
    
    i2c.unlock()
        
    gas_sensor = adafruit_sgp30.Adafruit_SGP30(i2c)
    temp_and_humidity_sensor = adafruit_ahtx0.AHTx0(i2c)
    display = adafruit_ht16k33.segments.Seg14x4(i2c)
    buzzer = pwmio.PWMOut(board.D10, duty_cycle = 0, frequency = 660)
    
    return gas_sensor, temp_and_humidity_sensor, display, buzzer

def display_values(values):
    global value_state
    if value_state == 0:
        display.print(f" {values[value_state]}")
    elif value_state == 1:
        display.print(f"   {values[value_state]}")
    elif value_state == 2:
        display.print(f"{values[value_state]:.1f}C")
    elif value_state == 3:
        display.print(f" {values[value_state]:.1f}")
    else:
        value_state = 0
    return

def read_values():
        CO2 = gas_sensor.eCO2
        TVOC = gas_sensor.TVOC
        temp = temp_and_humidity_sensor.temperature
        humidity = temp_and_humidity_sensor.relative_humidity
        return [CO2, TVOC, temp, humidity]
    

gas_sensor, temp_and_humidity_sensor, display, buzzer = start()

while True:
    
    # S1 Read values and send to comparison
    if state == 0:
        values = read_values()
        display_values(values)
        print(values)
        print(value_state)
        state = 1

    # S2 Compare values and send to delay or alarm
    elif state == 1:
        state = 2
        for i in range(len(values)):
            if values[i] > LIMITS[i]:
                state = 3
                value_state = i
                alarm = True
            
        display_values(values)

    elif state == 2:
        if alarm:
            delay_alarm()
        else:
            delay(2)
        
        value_state += 1
        state = 0

    elif state == 3:
        
        start_alarm()
        state = 2