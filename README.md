# Generación de Datos Simulados para Sensor de Radiación UV

Este script genera datos simulados de un sensor de radiación ultravioleta (UV) y los publica en un tópico de **Pub/Sub** de Google Cloud. Es utilizado como parte de una demostración para simular datos en tiempo real.

## Descripción del Script

El script realiza las siguientes funciones:
1. **Simulación de sensores**: Genera datos de 5 sensores virtuales con ubicaciones aleatorias.
2. **Generación de índices UV**: Calcula valores de índice UV con variaciones diurnas y añade ruido aleatorio para mayor realismo.
3. **Inserción de errores**: Simula fallos en los sensores con un 1% de probabilidad.
4. **Publicación en Pub/Sub**: Envía los datos simulados a un tópico de Pub/Sub para su posterior procesamiento.

### Principales Campos Generados:
- `timestamp`: Marca de tiempo en formato ISO.
- `sensor_id`: Identificador único para cada sensor.
- `uv_index`: Índice UV simulado.
- `latitude` y `longitude`: Coordenadas geográficas del sensor.
- `temperature`: Temperatura simulada entre 15°C y 35°C.
- `error_code`: Código de error (si ocurre un fallo en el sensor).

## Requisitos Previos

1. **Google Cloud SDK**: Instalar y configurar el SDK de Google Cloud.
2. **Cuenta de Servicio**: Asegúrate de tener una cuenta de servicio con permisos para Pub/Sub.
3. **Biblioteca de Python**: Instalar las dependencias necesarias ejecutando:
   ```bash
   pip install google-cloud-pubsub
    ```

## Ejecución del Script

### Configurar Variables

Abre el script `generate_uv_data.py` y ajusta las siguientes variables según tu proyecto:

```python
project_id = "TU_ID_DE_PROYECTO"
topic_id = "uv-data-topic"
```

### Ejecutar el Script
Desde tu terminal, navega al directorio donde está el script y ejecuta:

```bash
python generate_uv_data.py
```

## Estructura de Datos Enviados
A continuación, un ejemplo del formato JSON publicado en Pub/Sub:
```json
{
  "timestamp": "2024-12-04T12:34:56.789Z",
  "sensor_id": "sensor_1",
  "uv_index": 7.8,
  "latitude": -12.046374,
  "longitude": -77.042793,
  "temperature": 28.5,
  "error_code": null
}
```

## Configuración de Pub/Sub

En esta sección se describe cómo configurar **Pub/Sub** para que funcione con el script de generación de datos simulados.

### Tópico y Suscripción

- **Tópico:** `uv-data-topic`
- **Suscriptor:** `uv-data-topic-sub`

### Creación del Tópico

Para crear el tópico necesario, ejecuta el siguiente comando en la terminal de Google Cloud:
```python
gcloud pubsub topics create uv-data-topic
```
Este comando crea el tópico `uv-data-topic` en tu proyecto de Google Cloud.

### Creación de la Suscripción

Para configurar la suscripción, utiliza el siguiente comando:
```python
gcloud pubsub subscriptions create uv-data-topic-sub --topic=uv-data-topic
```
Esto vincula la suscripción `uv-data-topic-sub` al tópico `uv-data-topic`. Asegúrate de que el nombre de la suscripción coincida con lo configurado en tus aplicaciones.

### Notas Importantes

1. **Permisos:** Verifica que tu cuenta de servicio tenga permisos para trabajar con Pub/Sub. Los permisos mínimos necesarios son:
   - `pubsub.topics.publish` para publicar mensajes.
   - `pubsub.subscriptions.consume` para recibir mensajes.
2. **Configuración Regional:** Por defecto, Pub/Sub utiliza la región global. Si tu proyecto requiere una región específica, agrega la bandera `--message-storage-policy` con la región deseada al crear el tópico.

## Configuración y Ejecución de Dataflow

Esta sección describe cómo configurar y ejecutar el pipeline estándar de **Dataflow**, así como cómo personalizarlo con configuraciones manuales.

### Pipeline Estándar

El archivo `uv_dataflow_pipeline.py` realiza las siguientes operaciones:
1. **Lectura desde Pub/Sub**: Consume datos en tiempo real desde el tópico `uv-data-topic`.
2. **Escritura en Raw Layer**: Guarda los datos en bruto en Cloud Storage.
3. **Validación y Limpieza**: 
   - Verifica que los datos contengan todos los campos requeridos.
   - Convierte tipos de datos según sea necesario.
4. **Escritura en BigQuery**: 
   - Guarda datos enriquecidos en la tabla `enriched_data`.
   - Calcula promedios de índice UV y los almacena en la tabla `curated_data`.

### Requisitos Previos

1. **Apache Beam**: Instala las dependencias necesarias ejecutando:
   pip install apache-beam[gcp]
   
2. **Google Cloud Storage**: Asegúrate de que exista un bucket para almacenar los datos en bruto.
3. **BigQuery**: Crea las tablas `enriched_data` y `curated_data` con los siguientes esquemas:
   - `enriched_data`:
     - `timestamp: STRING`
     - `sensor_id: STRING`
     - `uv_index: FLOAT`
     - `latitude: FLOAT`
     - `longitude: FLOAT`
     - `temperature: FLOAT`
     - `error_code: STRING`
   - `curated_data`:
     - `sensor_id: STRING`
     - `avg_uv_index: FLOAT`

### Ejecución del Pipeline Estándar

Para ejecutar el pipeline estándar, usa el siguiente comando:
```python
python uv_dataflow_pipeline.py \
    --project nimble-climber-433101-b6 \
    --region us-central1 \
    --input_topic projects/nimble-climber-433101-b6/topics/uv-data-topic \
    --output_raw gs://capa_raw_pipeline/capa_raw_pipeline/output \
    --output_table nimble-climber-433101-b6:uv_dataset.enriched_data \
    --temp_location gs://capa_raw_pipeline/temp \
    --runner DataflowRunner
```
### Pipeline con Configuración Manual

El archivo `uv_dataflow_pipeline_manual.py` es una variación que permite configurar manualmente recursos como:
- Número de workers inicial y máximo.
- Tipo de máquina.
- Tamaño del disco persistente.
- Algoritmo de escalado.

### Diferencias del Código para Configuración Manual

El pipeline manual añade configuraciones como las siguientes:
```python
worker_options = pipeline_options.view_as(beam.options.pipeline_options.WorkerOptions)  
worker_options.num_workers = 2  # Número inicial de workers  
worker_options.max_num_workers = 5  # Máximo número de workers  
worker_options.machine_type = 'e2-medium'  # Tipo de máquina  
worker_options.disk_size_gb = 40  # Tamaño del disco persistente  
worker_options.autoscaling_algorithm = 'THROUGHPUT_BASED'  # Escalado basado en rendimiento  
```
### Ejecución del Pipeline Manual

Si necesitas personalizar el pipeline, usa el siguiente comando:

python uv_dataflow_pipeline_manual.py \
    --project nimble-climber-433101-b6 \
    --region us-central1 \
    --input_topic projects/nimble-climber-433101-b6/topics/uv-data-topic \
    --output_raw gs://capa_raw_pipeline/capa_raw_pipeline/output \
    --output_table nimble-climber-433101-b6:uv_dataset.enriched_data \
    --temp_location gs://capa_raw_pipeline/temp \
    --runner DataflowRunner

### Notas Importantes

1. **Permisos**: Asegúrate de que la cuenta de servicio tenga permisos para Pub/Sub, Dataflow, Cloud Storage y BigQuery.
2. **Configuración Automática vs Manual**:
   - Usa el pipeline estándar para configuraciones predeterminadas y despliegues rápidos.
   - Opta por el pipeline manual si necesitas personalizar recursos o optimizar costos.
