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

TVOC_LIMIT = 2000
CO2_LIMIT = 1000
TEMP_LIMIT = 32
HUMIDITY_LIMIT = 70

# initialize button
button = digitalio.DigitalInOut(board.D9)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# initalize I2C bus for stemma
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
i2c.try_lock()

# startvalues
value_state = 0
state = 0
button_pressed = False
alarm = False

def stop_alarm(buzzer):
    buzzer.deinit()
        
def start_alarm():
    buzzer = pwmio.PWMOut(board.D10, duty_cycle = 2 ** 10, frequency = 660)
    return buzzer
        
def delay(delay_time):
    global button_pressed
    start = time.monotonic()
    end = time.monotonic()
    while delay_time > time.monotonic() - start:
        if not button.value == True:
            button_pressed = True

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
    
    return gas_sensor, temp_and_humidity_sensor, display

def display_values(value):
    display.print(f" {value}")
    return

def read_values():
        CO2 = gas_sensor.eCO2
        TVOC = gas_sensor.TVOC
        temp = temp_and_humidity_sensor.temperature
        humidity = temp_and_humidity_sensor.relative_humidity
        return [CO2, TVOC, temp, humidity]
    

gas_sensor, temp_and_humidity_sensor, display = start()

while True:
    if state == 0:
        values = read_values()
        display_values(values)
        state = 1

    elif state == 1:
        if value in values > :
            state = 3
        else:
            state = 2

    elif state == 2:
        
        if not alarm:
            delay(1)
        else:
            delay(20)
        state = 3

    elif state == 3:
        start_alarm()
        state = 0