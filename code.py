import time
import board
import digitalio
import pwmio
import busio
import adafruit_ahtx0
import adafruit_sgp30

# Check to see if all modules are connected to the microcontroller

if busio.I2C.probe(0x38) == False:
    print("AHT20 sensor not found")
elif busio.I2C.probe(0x58) == False:
    print("SGP30 sensor not found")
elif busio.I2C.probe(0x36) == False:
    print("Rotary Encoder not found")

i2c_bus = busio.I2C(board.SCL, board.SDA, frequency=100000)

MOX_gas_sensor = adafruit_sgp30.Adafruit_SGP30(i2c_bus)

temp_and_humidity_sensor = adafruit_ahtx0.AHTx0(i2c_bus)

eCO2, TVOC = MOX_gas_sensor.iaq_measure()

temp, relative_humidity = temp_and_humidity_sensor.iaq_measure()


#i2c = board.STEMMA_I2C()

#temp_and_humidity_sensor = adafruit_ahtx0.AHTx0(i2c)

print(eCO2) 
print(TVOC)
print(temp)
print(relative_humidity)