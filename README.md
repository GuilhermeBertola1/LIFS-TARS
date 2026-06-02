# LIFS-TARS V2

## Visão Geral

O LIFS-TARS V2 é uma plataforma integrada para controle, monitoramento e aquisição de dados de reatores experimentais, combinando sistemas embarcados, comunicação MQTT, processamento espectral e interfaces web em tempo real.

O sistema foi desenvolvido para permitir:

* Monitoramento remoto dos reatores;
* Aquisição de dados espectrais;
* Controle operacional via navegador;
* Armazenamento de experimentos;
* Geração automática de relatórios;
* Comunicação em tempo real utilizando MQTT e Socket.IO.

---

## Arquitetura Geral

```text
ESP32 / Sensores
        │
        ▼
     MQTT Broker
        │
        ▼
+--------------------+
|      C_python      |
| MQTT → Socket.IO   |
+--------------------+
        │
        ├──────────────► controlsR1.com
        │
        ├──────────────► controlsR2.com
        │
        └──────────────► IntelMain.com

+--------------------+
|     lifsEspec      |
|  Espectrômetro     |
+--------------------+

+--------------------+
|      S_python      |
| Arquivos e PDFs    |
+--------------------+
```

## Estrutura

* IntelMain.com → Interface principal
* intel.com → Gestão de documentos
* controlsR1.com → Dashboard do Reator 1
* controlsR2.com → Dashboard do Reator 2
* C_python → Servidor MQTT/WebSocket
* S_python → Backend documental
* lifsEspec → Controle do espectrômetro
* lifsFlux → Controle de fluxo

## Tecnologias

* Python
* Flask
* Socket.IO
* MQTT
* Nginx
* Chart.js
* Bootstrap
* PySeaBreeze
* FPDF

## Licença

Projeto desenvolvido para pesquisa e aplicações laboratoriais.
