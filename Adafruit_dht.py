import requests
import time
from gpiozero import PWMLED
import RPi.GPIO as GPIO
import Adafruit_DHT

# GPIO beállítások: BCM számozást használunk.
GPIO.setmode(GPIO.BCM)

# DHT11 szenzor inicializálása
DHT_SENSOR = Adafruit_DHT.DHT11
# A DHT11 adatlába a GPIO17-re van kötve (citromsárga vezeték, fizikai 11. pin)
DHT_PIN = 17

# LED-ek beállítása a pontos bekötés alapján
# Piros LED (narancssárga vezeték) -> GPIO 21
# Kék LED (fehér vezeték) -> GPIO 20

red_led = PWMLED(21)    # Piros LED a GPIO 21-en (narancssárga vezeték)
blue_led = PWMLED(20)   # Kék LED a GPIO 20-on (fehér vezeték)

# ThingSpeak API kulcs – Saját, egyedi kulcs szükséges az adatküldéshez!
API_KEY = 'G6SD9SSNQ1VACKKH' # <-- Az én API kulcsom!

# Adatküldő függvény ThingSpeak-re
def send_data_to_thingspeak(temp, humid):
    url = f'https://api.thingspeak.com/update?api_key={API_KEY}&field1={temp}&field2={humid}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Sikeres adatküldés ThingSpeak-re: Hőmérséklet={temp:.1f}°C, Páratartalom={humid:.1f}%")
        else:
            print(f"Sikertelen adatküldés ThingSpeak-re: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Hiba az adatküldés során: {e}")

# Fő programciklus: Ez fut folyamatosan
try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        if humidity is not None and temperature is not None:
            print(f"Aktuális Hőmérséklet: {temperature:.1f}°C")
            print(f"Aktuális Páratartalom: {humidity:.1f}%")

            # LED logika: 20 fok alatt PIROS, felette KÉK
            if temperature <= 20:
                red_led.value = 1   # Piros LED be
                blue_led.value = 0  # Kék LED ki
            else:
                red_led.value = 0   # Piros LED ki
                blue_led.value = 1  # Kék LED be

            send_data_to_thingspeak(temperature, humidity)
        else:
            print("Sikertelen szenzoradat olvasás. Ellenőrizd a bekötést és a kódot.")
            time.sleep(2)

        time.sleep(10)

except KeyboardInterrupt:
    print("\nProgram leállítva a felhasználó által.")
    GPIO.cleanup()
    blue_led.close()
    red_led.close()

