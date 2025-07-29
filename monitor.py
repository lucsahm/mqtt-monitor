#!/usr/bin/env python3

import time
import paho.mqtt.client as mqtt
from datetime import datetime

last_heartbeat = None
timeout = 60  # segundos

def on_connect(client, userdata, flags, rc):
    print(f"🟢 Conectado ao broker com código de retorno: {rc}")
    client.subscribe("esp32/heartbeat")
    print("📡 Inscrito no tópico 'esp32/heartbeat'")

def on_message(client, userdata, message):
    global last_heartbeat
    last_heartbeat = datetime.now()
    print("💓 Heartbeat recebido:", last_heartbeat, "→", message.payload.decode())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.loop_start()

while True:
    print("⌛ Verificando...")
    if last_heartbeat:
        diff = (datetime.now() - last_heartbeat).total_seconds()
        if diff > timeout:
            print("❌ Sem heartbeat! Último há", int(diff), "segundos")
    time.sleep(10)

