import argparse
import json
import logging
from datetime import datetime

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.io.gcp.pubsub import ReadFromPubSub
from apache_beam.io import WriteToBigQuery
from apache_beam.transforms.window import FixedWindows
from apache_beam.io import fileio

def parse_pubsub_message(message):
    try:
        data = json.loads(message.decode('utf-8'))
        return data
    except json.JSONDecodeError:
        return None

def validate_and_clean(data):
    if data is None:
        return None

    required_fields = ['timestamp', 'sensor_id', 'uv_index', 'latitude', 'longitude', 'temperature']

    for field in required_fields:
        if field not in data or data[field] is None:
            return None

    try:
        data['uv_index'] = float(data['uv_index'])
        data['latitude'] = float(data['latitude'])
        data['longitude'] = float(data['longitude'])
        data['temperature'] = float(data['temperature'])
        data['timestamp'] = data['timestamp']
    except (ValueError, TypeError):
        return None

    return data

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_topic', required=True)
    parser.add_argument('--output_raw', required=True)
    parser.add_argument('--output_table', required=True)
    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(pipeline_args, save_main_session=True)
    pipeline_options.view_as(StandardOptions).streaming = True

    # Configuración manual de recursos
    worker_options = pipeline_options.view_as(beam.options.pipeline_options.WorkerOptions)
    worker_options.num_workers = 2  # Numero inicial de workers
    worker_options.max_num_workers = 5  # Maximo número de workers
    worker_options.machine_type = 'e2-medium'  # Tipo de maquina
    worker_options.disk_size_gb = 40  # Tamaño del disco persistente
    worker_options.autoscaling_algorithm = 'THROUGHPUT_BASED'  # Escalado basado en rendimiento

    with beam.Pipeline(options=pipeline_options) as p:
        messages = p | 'Leer de Pub/Sub' >> ReadFromPubSub(topic=known_args.input_topic)

        raw_data = (
            messages
            | 'Ventana para Datos en Bruto' >> beam.WindowInto(FixedWindows(60))
            | 'Preparar Datos en Bruto' >> beam.Map(lambda x: x.decode('utf-8'))
            | 'Escribir Datos en Bruto' >> fileio.WriteToFiles(
                path=known_args.output_raw,
                file_naming=fileio.default_file_naming(prefix='output', suffix='.txt')
            )
        )

        parsed = messages | 'Parsear Mensajes' >> beam.Map(parse_pubsub_message)

        cleaned = (
            parsed
            | 'Validar y Limpiar Datos' >> beam.Map(validate_and_clean)
            | 'Filtrar Datos Nulos' >> beam.Filter(lambda x: x is not None)
        )

        enriched = cleaned | 'Escribir a BigQuery' >> WriteToBigQuery(
            known_args.output_table,
            schema='timestamp:STRING,sensor_id:STRING,uv_index:FLOAT,latitude:FLOAT,longitude:FLOAT,temperature:FLOAT,error_code:STRING',
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
        )

        curated = (
            cleaned
            | 'Ventana para Datos Curados' >> beam.WindowInto(FixedWindows(60))
            | 'Clave por sensor_id' >> beam.Map(lambda x: (x['sensor_id'], x))
            | 'Agrupar por sensor_id' >> beam.GroupByKey()
            | 'Calcular Promedio UV' >> beam.Map(lambda kv: {
                'sensor_id': kv[0],
                'avg_uv_index': sum([elem['uv_index'] for elem in kv[1]]) / len(kv[1])
            })
            | 'Escribir Datos Curados' >> WriteToBigQuery(
                '{}:uv_dataset.curated_data'.format(pipeline_options.get_all_options().get('project')),
                schema='sensor_id:STRING,avg_uv_index:FLOAT',
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()






"""
python uv_dataflow_pipeline_manual.py \
    --project nimble-climber-433101-b6 \
    --region us-central1 \
    --input_topic projects/nimble-climber-433101-b6/topics/uv-data-topic \
    --output_raw gs://capa_raw_pipeline/capa_raw_pipeline/output \
    --output_table nimble-climber-433101-b6:uv_dataset.enriched_data \
    --temp_location gs://capa_raw_pipeline/temp \
    --runner DataflowRunner

"""