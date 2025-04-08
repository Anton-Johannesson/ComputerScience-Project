import time
import board
import busio
import digitalio
import adafruit_sgp30
import adafruit_ahtx0
#import adafruit_lps2x  # Om du vill använda trycksensorn
from adafruit_display_text import label
import displayio
import terminalio
from digitalio import DigitalInOut, Direction, Pull

# ---- Konfiguration av I2C ----
i2c = busio.I2C(board.SCL, board.SDA)

# ---- Initiera sensorer ----
# Luftkvalitetssensor (SGP30)
try:
    sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
    # Initiera baslinje (detta görs vanligtvis första gången under en kort period)
    sgp30.start_measurement()
except Exception as e:
    print("SGP30 kunde inte initieras:", e)
    sgp30 = None

# Temperatur & fuktighetssensor (AHT20)
try:
    aht20 = adafruit_ahtx0.AHTx0(i2c)
except Exception as e:
    print("AHT20 kunde inte initieras:", e)
    aht20 = None

# ---- Konfigurera display (exempel med en I2C-baserad alfanumerisk display) ----
# För detta exempel använder vi displayio för att skapa en enkel textvisning
display = board.DISPLAY  # om du t.ex. har en inbyggd display (annars behöver du konfigurera en extern via I2C)

# Skapa en huvudgrupp för displayinnehåll
splash = displayio.Group()
display.show(splash)

# Skapa bakgrundsfärg (svart)
color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000  # svart
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Skapa ett textlabel för att visa mätvärden
text_area = label.Label(terminalio.FONT, text="Initierer...", color=0xFFFFFF)
text_area.x = 10
text_area.y = 20
splash.append(text_area)

# ---- Konfigurera Rotary Encoder (enkel knappexempel) ----
# Exempel: anta att en knapp är kopplad till pin D5
button = DigitalInOut(board.D5)
button.direction = Direction.INPUT
button.pull = Pull.UP  # om knappen drar ner spänningen vid tryck

# ---- Konfigurera LED och buzzer för varningar ----
led = DigitalInOut(board.D6)
led.direction = Direction.OUTPUT

buzzer = DigitalInOut(board.D7)
buzzer.direction = Direction.OUTPUT

# ---- Definiera tröskelvärden för larm ----
# Exempelvärden – justera efter experiment
VOC_THRESHOLD = 500  # exempelvärde för VOC, beroende på sensorens kalibrering
TEMP_LOW = 15.0      # minimitemperatur (grader Celsius)
TEMP_HIGH = 28.0     # hög temperatur

# ---- Hjälpfunktioner ----
def update_display(message: str):
    text_area.text = message

def check_alerts():
    alert_triggered = False
    messages = []
    
    # Luftkvalitet: Om TVOC över tröskelvärdet
    if sgp30 is not None:
        # sgp30.TVOC anges i ppb
        if sgp30.TVOC and sgp30.TVOC > VOC_THRESHOLD:
            alert_triggered = True
            messages.append("Dålig luft!")
    
    # Temperaturkontroll
    if aht20 is not None:
        temp = aht20.temperature
        if temp < TEMP_LOW or temp > TEMP_HIGH:
            alert_triggered = True
            messages.append(f"Temp: {temp:.1f}C")
    
    # (Lägg till fler kontroller vid behov, t.ex. luftfuktighet, tryck etc.)
    return alert_triggered, " | ".join(messages)

# ---- Huvudloopen ----
last_update = time.monotonic()

while True:
    # Läs sensorvärden
    sensor_message = ""
    
    # Läs från SGP30
    if sgp30 is not None:
        tvoc = sgp30.TVOC if sgp30.TVOC is not None else 0
        eco2 = sgp30.eCO2 if sgp30.eCO2 is not None else 0
        sensor_message += f"VOC: {tvoc} ppb, eCO2: {eco2} ppm\n"
    
    # Läs från AHT20
    if aht20 is not None:
        temp = aht20.temperature
        humidity = aht20.relative_humidity
        sensor_message += f"Temp: {temp:.1f} C, Fukt: {humidity:.1f}%\n"
    
    # (Eventuellt: Läs från LPS22 om installerad)
    
    # Kolla för varningar
    alarm, alert_msg = check_alerts()
    if alarm:
        sensor_message += "ALARM: " + alert_msg
        led.value = True    # Tänd LED
        buzzer.value = True # Aktivera buzzer (kan förbättras med PWM och ljudsekvenser)
    else:
        led.value = False
        buzzer.value = False
    
    # Uppdatera displayen varannan sekund
    current_time = time.monotonic()
    if current_time - last_update > 2:
        update_display(sensor_message)
        last_update = current_time
    
    # Hantera knapptryck (exempel: tryck ger en "ack" på alarmet eller ändrar läge)
    if not button.value:  # om knappen trycks (pull‑up så false betyder nedtryckt)
        update_display("Knapp tryckt, återställer larm...")
        time.sleep(1)   # debounce effekt
        # Här kan du lägga in logik för att stänga av larmet eller ändra tröskelvärden
    time.sleep(0.1)
