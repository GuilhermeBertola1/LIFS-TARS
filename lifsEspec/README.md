# lifsEspec

## Objetivo

Integração entre o sistema LIFS-TARS e o espectrômetro Ocean Insight.

## Funcionalidades

* Aquisição espectral;
* Configuração do tempo de integração;
* Operação por trigger externo;
* Publicação MQTT.

## Dependências

```bash
pip install pyseabreeze
pip install numpy
pip install paho-mqtt
```

## Modos

### Free Running

Aquisição contínua.

### External Trigger

Aquisição sincronizada por trigger externo.

## Dados Publicados

* Comprimentos de onda
* Intensidade espectral
* Estado do equipamento
