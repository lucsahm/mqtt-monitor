#!/usr/bin/env python3

"""
Monitor MQTT de Heartbeat para ESP8266

Este script conecta-se a um broker MQTT e monitora mensagens de heartbeat enviadas 
pelo dispositivo ESP8266 no tópico "esp8266/heartbeat". 

- Recebe mensagens JSON que indicam o status do dispositivo ("online" ou "offline").
- Registra o timestamp do último heartbeat válido ("online").
- Caso não receba um heartbeat dentro do tempo limite (60 segundos), publica repetidamente 
  uma mensagem de alerta com status "offline" a cada 30 segundos no mesmo tópico.
- Ao receber novamente um heartbeat "online", reseta o monitoramento e interrompe os alertas "offline".

O objetivo é permitir o monitoramento confiável e automático da conectividade do dispositivo remoto.
"""

import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

last_heartbeat = None
timeout = 60  # segundos

TOPIC_SUB = "esp8266/heartbeat"

offline_interval = 30  # segundos entre alertas offline repetidos
last_offline_publish = None  # hora do último envio offline

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"✅ Conectado ao broker MQTT com código {rc}")
    client.subscribe(TOPIC_SUB)
    print(f"📡 Inscrito no tópico: {TOPIC_SUB}")

def on_message(client, userdata, msg):
    global last_heartbeat, last_offline_publish
    try:
        payload = json.loads(msg.payload.decode())
        status = payload.get("status")
        device = payload.get("device")

        if device == "esp8266":
            if status == "online":
                last_heartbeat = datetime.now(timezone.utc)
                last_offline_publish = None  # reseta controle de envio offline
                print(f"💓 Heartbeat válido recebido: {payload}")
            elif status == "offline":
                print(f"⚠️ Dispositivo reportou offline: {payload}")
            else:
                print(f"⚠️ Status desconhecido: {payload}")
        else:
            print(f"⚠️ Mensagem de dispositivo desconhecido: {payload}")

    except Exception as e:
        print(f"❌ Erro ao processar mensagem: {e}")

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

print("🔌 Conectando ao broker MQTT...")
client.connect("broker.hivemq.com", 1883, 60)
client.loop_start()

while True:
    now = datetime.now(timezone.utc)
    if last_heartbeat:
        diff = (now - last_heartbeat).total_seconds()
        if diff > timeout:
            if (last_offline_publish is None) or ((now - last_offline_publish).total_seconds() > offline_interval):
                alert = {
                    "device": "esp8266",
                    "status": "offline",
                    "timestamp": now.isoformat()
                }
                print(f"⚠️ Timeout detectado ({diff:.1f}s). Publicando alerta de offline: {alert}")
                client.publish(TOPIC_SUB, payload=json.dumps(alert), qos=1)
                last_offline_publish = now
    time.sleep(5)
