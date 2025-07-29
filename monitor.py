#!/usr/bin/env python3

import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

last_heartbeat = None
timeout = 60  # segundos

TOPIC_SUB = "esp32/heartbeat"
TOPIC_PUB = "esp32/heartbeat/response"

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"✅ Conectado ao broker MQTT com código de resultado {rc}")
    client.subscribe(TOPIC_SUB)
    print(f"📡 Inscrito no tópico: {TOPIC_SUB}")

def on_message(client, userdata, msg):
    global last_heartbeat
    last_heartbeat = datetime.now(timezone.utc)
    response = {
        "response": "pong",
        "timestamp": last_heartbeat.isoformat()
    }
    print(f"💓 Heartbeat recebido: {msg.payload.decode()} → Respondendo com: {response}")
    client.publish(TOPIC_PUB, payload=json.dumps(response))

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

print("🔌 Conectando ao broker MQTT...")
client.connect("broker.hivemq.com", 1883, 60)
client.loop_start()

while True:
    if last_heartbeat:
        diff = (datetime.now(timezone.utc) - last_heartbeat).total_seconds()
        if diff > timeout:
            alert = {
                "response": "sem heartbeat",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            print(f"⚠️ Timeout detectado ({diff:.1f}s). Publicando alerta: {alert}")
            client.publish(TOPIC_PUB, payload=json.dumps(alert))
    time.sleep(10)
