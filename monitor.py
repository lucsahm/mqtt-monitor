import json
from datetime import datetime, timezone
import threading
import paho.mqtt.client as mqtt
from flask import Flask

# Configurações MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_RECEIVE = "sahm/heartbeat"
TOPIC_RESPONSE = "sahm/heartbeat/response"

# Função chamada quando uma mensagem é recebida
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode().strip()
        print(f"💓 Heartbeat recebido: {payload}")
        if payload.lower() == "heartbeat":
            now = datetime.now(timezone.utc).isoformat()
            response = {
                "response": "pong",
                "timestamp": now
            }
            client.publish(TOPIC_RESPONSE, json.dumps(response))
    except Exception as e:
        print("Erro ao processar mensagem:", e)

# Função que roda o loop MQTT
def mqtt_loop():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.subscribe(TOPIC_RECEIVE)
    client.loop_forever()

# Inicia o monitor MQTT em uma thread
threading.Thread(target=mqtt_loop, daemon=True).start()

# Flask para manter uma porta aberta no Render
app = Flask(__name__)

@app.route('/')
def status():
    return "MQTT Monitor rodando com Flask + MQTT.", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
