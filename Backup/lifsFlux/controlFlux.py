import serial
import time
import paho.mqtt.client as mqtt

# ====== CONFIG ======
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 9600
MQTT_BROKER = '192.168.0.100'
MQTT_PORT = 1883
MQTT_TOPIC = 'teste/canal'
# ====================

# Abre serial
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)  # tempo para Arduino resetar

def on_connect(client, userdata, flags, rc):
    print("Conectado ao MQTT | rc =", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    comando = msg.payload.decode().strip()
    print("Recebido:", comando)

    # permite múltiplos comandos separados por ;
    comandos = comando.split(';')

    for cmd in comandos:
        cmd = cmd.strip()
        if cmd:
            ser.write((cmd + '\n').encode())
            time.sleep(0.1)

# Cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("Sistema pronto. Aguardando comandos MQTT...")
client.loop_forever()
