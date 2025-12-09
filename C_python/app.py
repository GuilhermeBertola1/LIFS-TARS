import eventlet
import eventlet.wsgi
eventlet.monkey_patch()
from flask import Flask
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')

# ========== MQTT Setup ==========
def on_connect(client, userdata, flags, rc):
    print("Conectado ao broker MQTT com código", rc)
    client.subscribe("reator1/#")
    client.subscribe("reator2/#")
    client.subscribe("espectrometro/#")

def on_message(client, userdata, msg):
    topico = msg.topic
    reator_num = '1' if 'reator1' in topico else '2'

    if "temperatura" in topico:
        dado = msg.payload.decode()
        socketio.emit(f"temperatura_r{reator_num}", {"valor": dado})
    elif "pressao" in topico:
        dado = msg.payload.decode()
        socketio.emit(f"pressao_r{reator_num}", {"valor": dado})
    elif "espessura" in topico:
        dado = msg.payload.decode()
        socketio.emit(f"espessura_r{reator_num}", {"valor": dado})
    elif "tempagua" in topico:
        dado = msg.payload.decode()
        socketio.emit(f"tempagua_r{reator_num}", {"valor": dado})
    elif "espectrometro_w" in topico:
        socketio.emit(f"espectrometro_r{reator_num}_w", msg.payload)
    elif "espectrometro_int" in topico:
        socketio.emit(f"espectrometro_r{reator_num}_int", msg.payload)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("192.168.0.100", 1883, 60)

# ========== WebSocket ==========
@socketio.on("comando_r1")
def handle_comando_r1(data):
    acao = data["acao"]
    print(f"[COMANDO R1] Enviando via MQTT: {acao}")

    if acao in ["ligar", "desligar"]:
        # manda para o reator (ESP)
        mqtt_client.publish("reator1/comando", acao)
        # também manda para o espectrômetro
        mqtt_client.publish("espectrometro/comando", acao + "_r1")

    elif acao in ["Start", "Pause", "request_wavelengths"] or acao.startswith("set_integration"):
        # só espectrômetro
        mqtt_client.publish("espectrometro/comando", acao)

    else:
        # qualquer outro vai só pro reator
        mqtt_client.publish("reator1/comando", acao)

@socketio.on("comando_r2")
def handle_comando_r2(data):
    acao = data["acao"]
    print(f"[COMANDO R2] Enviando via MQTT: {acao}")

    if acao in ["ligar", "desligar"]:
        # manda para o reator (ESP)
        mqtt_client.publish("reator2/comando", acao)
        # também manda para o espectrômetro
        mqtt_client.publish("espectrometro/comando", acao + "_r2")

    elif acao in ["Start", "Pause", "request_wavelengths"] or acao.startswith("set_integration"):
        # só espectrômetro
        mqtt_client.publish("espectrometro/comando", acao)

    else:
        # qualquer outro vai só pro reator
        mqtt_client.publish("reator2/comando", acao)

if __name__ == "__main__":
    mqtt_client.loop_start()  # Inicia o loop assim que o app inicia
    print("Running r1 on: http://192.168.0.101:120/")
    print("Running r2 on: http://192.168.0.101:130/")
    socketio.run(app, host="0.0.0.0", port=6000, debug=False, use_reloader=False)