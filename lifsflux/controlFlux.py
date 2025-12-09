import serial
import time
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
        print("Conectado! codigo rc: ",rc)
        client.subscribe("teste/canal")

def on_message(client, userdata, msg):
        print("mensagem recebida")

ser = serial.Serial('/dev/ttyUSB0',9600)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.0.100",1883,60)

time.sleep(2)
ser.write(b"CH1 28\n")
time.sleep(0.1)
ser.write(b"CH1 ON\n")


ser.write(b"CH2 30\n")
time.sleep(0.1)
ser.write(b"CH2 OFF\n")


ser.write(b"CH3 29\n")
time.sleep(0.1)
ser.write(b"CH3 ON\n")


ser.write(b"CH4 80\n")
time.sleep(0.1)
ser.write(b"CH4 ON\n")
#ser.close()

client.loop_start()