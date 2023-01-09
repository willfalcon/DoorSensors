import MyPiAnalog
from guizero import App, Text
from gpiozero import DigitalOutputDevice, LED
#import paho.mqtt.client as paho
from requests import post, get
import json
import time


back_door = MyPiAnalog.MyPiAnalog(18, 23)
door_open_led = LED(24)
door_closed_led = LED(25)

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0OTIyYjIzMTMwMTU0YzMyOTk0ZGE4NzEyMDdmOThjMSIsImlhdCI6MTY3MzI0MDY3NCwiZXhwIjoxOTg4NjAwNjc0fQ.ztstpmQNg-lz5niFoPlZZz-WDiTKOZAwZFFS8HQFVIw",
    "content-type": "application/json",
}

def update_res():
    resistance = back_door.read_resistance()
    if resistance != 'infinite':
        door_open_led.off()
        door_closed_led.on()
        if resistance < 3000:
            resistance = 'Tamper!'
        else:
            resistance = "%.2f" % resistance + " ohms" # Round to 2 d.p.
            #ret= client1.publish("house/closet_door","closed")              #publish
            #send door closed message
            response = post(
                "http://192.168.86.195:8123/api/states/sensor.closet_door",
                headers=headers,
                data=json.dumps({"state": "closed", "attributes": {"friendly_name": "Closet Door"}})
            )
            print(response.text)
    else:
        door_open_led.on()
        door_closed_led.off()
        resistance = "Door is open"
        #ret= client1.publish("house/closet_door","open")                   #publish
        response = post(
            "http://192.168.86.195:8123/api/states/sensor.closet_door",
            headers=headers,
            data=json.dumps({"state": "open", "attributes": {"friendly_name": "Closet Door"}})
        )
        print(response)

    back_text.value = resistance

    state = get("http://192.168.86.195:8123/api/states/sensor.closet_door",
    headers=headers)
    back_text.after(1000, update_res)


# Create the GUI
app = App(title = "Thermometer", width="400", height="300")
Text(app, text="Resistance", size=32)
back_text = Text(app, text="0.00 ohms", size=25)
back_text.after(1000, update_res)
app.display()