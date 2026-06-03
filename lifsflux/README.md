# lifsFlux

## Objetivo

Módulo responsável pelo controle de vazão e comunicação serial com dispositivos externos.

## Recursos

* Controle de fluxo;
* Configuração de canais;
* Comunicação serial;
* Integração MQTT.

## Hardware

* ESP32
* Arduino
* Controladores de fluxo

## Comunicação

```text
MQTT
  │
  ▼
Python
  │
  ▼
Serial
  │
  ▼
Controlador
```

## Configurações

Porta serial:

```python
/dev/ttyUSB0
```

Baudrate:

```python
9600
```
