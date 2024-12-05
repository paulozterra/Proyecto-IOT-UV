import time
import json
import random
from datetime import datetime
from math import sin, pi
from google.cloud import pubsub_v1

# Configuración del cliente de Pub/Sub
project_id = "nimble-climber-433101-b6"
topic_id = "uv-data-topic"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

def generate_uv_data():
    base_time = datetime.utcnow()
    sensor_ids = [f"sensor_{i}" for i in range(1, 6)]  # 5 sensores
    latitudes = [random.uniform(-90, 90) for _ in sensor_ids]
    longitudes = [random.uniform(-180, 180) for _ in sensor_ids]

    while True:
        for sensor_id, lat, lon in zip(sensor_ids, latitudes, longitudes):
            current_time = datetime.utcnow()

            # Simulacion de variacion diurna del indice UV
            uv_index = max(0, 11 * sin(pi * (current_time.hour + current_time.minute / 60) / 12))
            uv_index += random.uniform(-1, 1)  # Ruido aleatorio

            # Simulacion de posibles errores
            error_code = None
            if random.random() < 0.01:  # 1% de probabilidad de error
                uv_index = None
                error_code = "SENSOR_MALFUNCTION"

            data = {
                "timestamp": current_time.isoformat(),
                "sensor_id": sensor_id,
                "uv_index": uv_index,
                "latitude": lat,
                "longitude": lon,
                "temperature": random.uniform(15, 35),
                "error_code": error_code
            }

            # Enviar datos a Pub/Sub
            future = publisher.publish(topic_path, json.dumps(data).encode("utf-8"))
            print(f"Enviado: {data}")
            time.sleep(1)  # Esperar 1 segundo entre lecturas

try:
    generate_uv_data()
except KeyboardInterrupt:
    print("Generación de datos detenida.")
