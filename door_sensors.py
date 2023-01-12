import MyPiAnalog
from guizero import App, Text
from gpiozero import DigitalOutputDevice, LED
#import paho.mqtt.client as paho
from requests import post, get
import json
import time
from readSecrets import read_secrets
import sched, time

back_door = MyPiAnalog.MyPiAnalog(18, 23)
door_open_led = LED(24)
door_closed_led = LED(25)

secrets = read_secrets()
headers = {
    "Authorization": "Bearer " + secrets["HOME_ASSISTANT_TOKEN"],
    "content-type": "application/json",
}

def update_door(sc):

    old_state = get("http://192.168.86.195:8123/api/states/sensor.closet_door", headers=headers)
    old_state = json.loads(old_state.text)['state']
    #print(old_state)
    resistance = back_door.read_resistance()
    if resistance != "infinite":
        if resistance < 3000:
            resistance = "Tamper!"
            if old_state != "tamper":
                response = post(
                    "http://192.168.86.195:8123/api/states/sensor.closet_door",
                    headers=headers,
                    data=json.dumps({"state": "tamper", "attributes": {"friendly_name": "Closet Door"}})
                )
        else:
            if old_state != "closed":
                resistance = "%.2f" % resistance + " ohms" # Round to 2 d.p.
                response = post(
                    "http://192.168.86.195:8123/api/states/sensor.closet_door",
                    headers=headers,
                    data=json.dumps({"state": "closed", "attributes": {"friendly_name": "Closet Door"}})
                )
    else:
        if old_state != "open":
            resistance = "Door is open"
            response = post(
                "http://192.168.86.195:8123/api/states/sensor.closet_door",
                headers=headers,
                data=json.dumps({"state": "open", "attributes": {"friendly_name": "Closet Door"}})
            )

    sc.enter(1, 1, update_door, (sc,))

s = sched.scheduler(time.time, time.sleep)

s.enter(1, 1, update_door, (s,))
s.run()
  #  back_text.value = resistance

   # back_text.after(1000, update_res)
#update_door()

#Create the GUI
#app = App(title = "Thermometer", width="400", height="300")
#Text(app, text="Resistance", size=32)
#back_text = Text(app, text="0.00 ohms", size=25)
#back_text.after(1000, update_res)
#app.display()