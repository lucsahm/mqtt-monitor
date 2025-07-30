/*
ESP8266 MQTT Heartbeat Monitor com Ping e Configuração WiFi via Access Point

Este código para ESP8266 realiza as seguintes funções:

- Conecta-se automaticamente à rede WiFi previamente configurada, ou cria um Access Point 
  chamado "ESP-AP" para configuração caso um botão (pino D5) seja pressionado no boot.
- Permite configurar o tópico MQTT através da página do Access Point.
- Conecta-se a um broker MQTT (broker.hivemq.com) no tópico configurado (padrão "esp8266/heartbeat").
- A cada 30 segundos, realiza um "ping" simples ao domínio "google.com" para medir a latência da conexão.
- Publica no tópico MQTT um payload JSON contendo:
    - Identificação do dispositivo ("esp8266"),
    - Status ("online"),
    - Tempo de resposta do ping em milissegundos (ou -1 em caso de erro),
    - Timestamp (milissegundos desde o boot).
- Garante reconexão automática ao broker MQTT caso a conexão seja perdida.

Este projeto permite monitorar a conectividade do dispositivo e da rede WiFi via MQTT de forma configurável e automatizada.
*/

#include <ESP8266WiFi.h>
#include <WiFiManager.h> // https://github.com/tzapu/WiFiManager
#include <MQTTClient.h>

WiFiClient net;
MQTTClient client;

#define MQTT_BROKER "broker.hivemq.com"
#define MQTT_PORT 1883

// Variáveis globais
char mqttTopic[64] = "esp8266/heartbeat"; // valor padrão
unsigned long lastPublish = 0;
const unsigned long interval = 30000;

// Pino para forçar modo AP (botão)
#define TRIGGER_PIN D5  // GPIO 14

WiFiManagerParameter custom_topic("topic", "MQTT Topic", mqttTopic, 64);

void connectMQTT() {
  while (!client.connected()) {
    Serial.print("Conectando ao broker MQTT...");
    if (client.connect("esp8266-client")) {
      Serial.println("conectado!");
    } else {
      Serial.print("falhou, rc=");
      Serial.print(client.lastError());
      Serial.println(" tentando novamente em 5 segundos...");
      delay(5000);
    }
  }
}

long pingGoogle() {
  IPAddress remote_ip;
  if (!WiFi.hostByName("google.com", remote_ip)) {
    return -1;
  }

  WiFiClient pingClient;
  unsigned long start = millis();
  if (!pingClient.connect(remote_ip, 80)) {
    return -1;
  }
  unsigned long end = millis();
  pingClient.stop();
  return end - start;
}

void setup() {
  Serial.begin(115200);

  // Configura pino do botão
  pinMode(TRIGGER_PIN, INPUT_PULLUP);

  WiFiManager wm;
  wm.addParameter(&custom_topic);  // Adiciona campo para tópico MQTT

  // Se botão pressionado no boot, forçar modo AP
  if (digitalRead(TRIGGER_PIN) == LOW) {
    Serial.println("Botão pressionado. Entrando em modo AP...");
    wm.resetSettings(); // Limpa WiFi salvo
    wm.startConfigPortal("ESP-AP");
  } else {
    if (!wm.autoConnect("ESP-AP")) {
      Serial.println("Falha ao conectar. Reiniciando...");
      ESP.restart();
    }
  }

  // Lê valor digitado no portal
  strncpy(mqttTopic, custom_topic.getValue(), sizeof(mqttTopic));
  mqttTopic[sizeof(mqttTopic)-1] = '\0'; // garante fim de string

  Serial.println("WiFi conectado!");
  Serial.print("Usando tópico MQTT: ");
  Serial.println(mqttTopic);

  client.begin(MQTT_BROKER, MQTT_PORT, net);
  // Adiciona o LWT (mensagem enviada se o ESP cair)
  client.setWill(mqttTopic, "{\"device\":\"esp8266\",\"status\":\"offline\"}", true, 1);
  connectMQTT();
}

void loop() {
  client.loop();

  if (!client.connected()) {
    connectMQTT();
  }

  if (millis() - lastPublish > interval) {
    lastPublish = millis();

    long pingTime = pingGoogle();
    if (pingTime < 0) {
      pingTime = -1;  // Timeout ou erro
    }

    String payload = "{\"device\":\"esp8266\",\"status\":\"online\",\"ping_ms\":" + String(pingTime) + ",\"timestamp\":" + String(millis()) + "}";
    bool sent = client.publish(mqttTopic, payload, 1, false);

    if (sent) {
      Serial.println("Mensagem publicada:");
    } else {
      Serial.println("Erro ao publicar.");
    }
    Serial.println(payload);
  }
}
