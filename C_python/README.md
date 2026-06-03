# C_python

## Objetivo

Servidor central responsável por interligar o broker MQTT às interfaces web.

## Responsabilidades

* Receber mensagens MQTT;
* Processar dados dos reatores;
* Distribuir eventos em tempo real;
* Gerenciar conexões Socket.IO.

## Fluxo

```text
MQTT Broker
     │
     ▼
 Flask + MQTT
     │
     ▼
 Socket.IO
     │
     ▼
 Navegadores
```

## Arquivos Principais

* app.py
* mqtt_handler.py
* socket_events.py

## Dependências

```bash
pip install flask
pip install flask-socketio
pip install eventlet
pip install paho-mqtt
```

## Eventos Emitidos

* temperatura_r1
* temperatura_r2
* pressao_r1
* pressao_r2
* espessura_r1
* espessura_r2
* espectrometro_r1
* espectrometro_r2
