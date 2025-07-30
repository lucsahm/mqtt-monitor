# ESP8266 MQTT Heartbeat Monitor com Ping

Projeto para monitorar a conectividade e latência da rede WiFi usando um ESP8266 e MQTT.

---

## Descrição

Este projeto conecta um ESP8266 a uma rede WiFi e a um broker MQTT público (broker.hivemq.com). Ele envia periodicamente mensagens de "heartbeat" contendo o tempo de resposta (ping) para o domínio google.com. O código inclui também uma interface de configuração via Access Point que permite configurar o WiFi e o tópico MQTT.

### Funcionalidades principais

- **Conexão WiFi automática:** conecta-se à rede previamente configurada.
- **Modo Access Point configurável:** segura o botão no boot para forçar o ESP8266 a criar um AP para configurar WiFi e tópico MQTT.
- **Publicação MQTT:** envia a cada 30 segundos um JSON com o status do dispositivo e o tempo de ping.
- **Reconexão automática:** reconecta ao broker MQTT caso a conexão seja perdida.

---

## Componentes usados

- Placa ESP8266 (ex: NodeMCU)
- Biblioteca [WiFiManager](https://github.com/tzapu/WiFiManager) para configuração WiFi via AP
- Biblioteca [MQTTClient](https://github.com/256dpi/arduino-mqtt) para comunicação MQTT
- Arduino IDE para programação

---

## Configuração e uso

1. Faça upload do código para o seu ESP8266 usando Arduino IDE.
2. No boot, segure o botão conectado ao pino D5 (GPIO14) para entrar no modo Access Point de configuração.
3. Conecte-se ao AP chamado `ESP-AP` com seu celular ou computador.
4. Abra o navegador e acesse `192.168.4.1`.
5. Configure sua rede WiFi e o tópico MQTT desejado (padrão: `esp8266/heartbeat`).
6. Salve e o ESP8266 irá conectar-se à rede WiFi e ao broker MQTT automaticamente.
7. O dispositivo enviará um JSON com status e tempo de ping a cada 30 segundos para o tópico configurado.

Exemplo do payload JSON publicado:
```json
{
  "device": "esp8266",
  "status": "online",
  "ping_ms": 23,
  "timestamp": 12345678
}
```

## Dependências de Bibliotecas

  WiFiManager
  MQTTClient
  ESP8266WiFi

As bibliotecas podem ser instaladas via Arduino IDE pelo Gerenciador de Bibliotecas.
