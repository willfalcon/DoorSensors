import RPi.GPIO as GPIO
import time, math

class MyPiAnalog:

    a_pin = 18
    b_pin = 23
    C = 0.0
    R1 = 0.0
    Vt = 0.0
    Vs = 0.0
    T5 = 0.0

    def __init__(self, a_pin = 18, b_pin = 23, C=0.33, R1=1000.0, Vt = 1.346, Vs = 3.25):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.a_pin = a_pin
        self.b_pini = b_pin
        self.C = C
        self.R1 = R1
        self.Vt = Vt
        self.Vs = Vs
        self.T5 = (C * R1 * 5) / 1000000.0
    # empty the capacitor ready to start filling it up

    def discharge(self):
        GPIO.setup(self.a_pin, GPIO.IN)
        GPIO.setup(self.b_pin, GPIO.OUT)
        GPIO.output(self.b_pin, False)
        time.sleep(self.T5) # 5T for 99% discharge

    # return the time taken for the voltage on the capacitor to count as a digital input HIGH
    def charge_time(self):
        GPIO.setup(self.b_pin, GPIO.IN)
        GPIO.setup(self.a_pin, GPIO.OUT)
        GPIO.output(self.a_pin, True)
        t1 = time.time()
        while not GPIO.input(self.b_pin):
            if time.time() - t1 > 0.01:
                break
            else:
                pass
        t2 = time.time()
        elapsed = (t2 - t1) * 1000000 # microseconds
        if elapsed >= 10000:
           return 'infinite'
        return elapsed

    # Take an analog reading as the time taken to charge after first discharging the capacitor
    def analog_read(self):
        self.discharge()
        t = self.charge_time()
        self.discharge()
        return t

    # Convert the time taken to charge the cpacitor into a value of resistance
    # To reduce errors in timing, do it a few times and take the median value.
    def read_resistance(self):
        n = 7
        readings = []
        infinites = []
        for i in range(0, n):
            reading = self.analog_read()
            if reading != 'infinite':
                readings.append(reading)
            else:
                infinites.append(reading)
            readings.sort()
        if len(infinites) >= 4:
            return 'infinite'
        t = readings[int(len(readings) / 2)]
        T = -t / math.log(1.0 - (self.Vt / self.Vs))
        RC = T
        r = (RC / self.C) - self.R1
        return r