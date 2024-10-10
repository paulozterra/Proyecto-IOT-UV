# Proyecto: Pipeline ETL en Streaming para Datos de Radiación Ultravioleta utilizando Google Cloud Platform

## Integrantes del Grupo
- Cuaresma Puclla Paulo Oshualdo
- Carhuancho Espejo Eros Joaquin

## Resumen del Proyecto

El proyecto consiste en la creación de un pipeline ETL (Extract, Transform, Load) en streaming para procesar datos de radiación ultravioleta en tiempo real. Los datos se obtienen a través de un sensor de radiación UV o, en su defecto, mediante una API que proporciona datos en streaming. El pipeline procesa estos datos en varias etapas, aplicando transformaciones y almacenándolos en diferentes capas dentro de una arquitectura lakehouse.

El objetivo principal del proyecto es asegurar la calidad de los datos desde su captura hasta su almacenamiento final, utilizando tecnologías de Google Cloud Platform como Pub/Sub, Dataflow y BigQuery. Aunque el alcance actual del proyecto se limita al desarrollo del pipeline ETL, se prevé que los datos procesados puedan ser utilizados para análisis avanzados y la creación de modelos predictivos en el futuro. Este pipeline será capaz de alimentar aplicaciones que proporcionen recomendaciones a los usuarios sobre las medidas de protección que deben tomar según los niveles de radiación UV detectados.



## Funcionalidades, características y arquitectura

### Funcionalidades principales

- **Ingesta de datos IoT en tiempo real**:  
  El pipeline captura datos de radiación ultravioleta desde un sensor IoT o mediante una API en tiempo real utilizando Google Cloud Pub/Sub. Esto asegura que los datos estén disponibles de forma continua para su procesamiento.

- **Transformación y enriquecimiento de datos**:  
  Los datos se procesan en Google Cloud Dataflow (Apache Beam), donde se validan, limpian y enriquecen. Se eliminan datos corruptos y se calculan métricas clave como promedios o picos de radiación en ventanas de tiempo.

- **Almacenamiento en capas (raw, enriched, curated)**:  
  Se sigue un enfoque lakehouse para almacenar los datos en tres capas:
  - **Raw**: Almacenamiento en Google Cloud Storage de los datos sin procesar, organizados por fecha.
  - **Enriched**: Datos enriquecidos, listos para análisis, almacenados en BigQuery.
  - **Curated**: Datos finales depurados, optimizados para consultas rápidas en BigQuery.

- **Escalabilidad**:  
  El pipeline se adapta automáticamente al volumen de datos, utilizando el autoescalado de Google Cloud Dataflow.

- **Monitoreo y alertas**:  
  Se utilizan Google Cloud Monitoring y Logging para generar alertas en caso de fallos o retrasos en el pipeline.


### Arquitectura

La arquitectura del proyecto sigue un enfoque por capas:

1. **Ingesta**:  
   - **Pub/Sub**: Captura de datos en tiempo real desde sensores IoT o APIs externas.

2. **Procesamiento**:  
   - **Dataflow (Apache Beam)**: Limpieza, transformación y enriquecimiento de los datos antes de su almacenamiento.

3. **Almacenamiento**:  
   - **Cloud Storage (Capa Raw)**: Almacena los datos sin procesar.
   - **BigQuery (Capas Enriched y Curated)**: Almacena los datos transformados y depurados para análisis.

4. **Monitoreo y alertas**:  
   - **Cloud Monitoring & Logging**: Supervisa el rendimiento y la salud del pipeline, configurando alertas en caso de fallos.

![Diagrama de arquitectura](Arquitectura.svg)

## Pasos necesarios para poder ejecutar su aplicación

## Pasos para ejecutar el proyecto

### 1. Configurar componentes IoT
- Conectar el **sensor GUVA-S12SD** al pin 34 del ESP32 para medir radiación UV.
- Conectar el **Display OLED SSD1306** a los pines I2C del ESP32 para mostrar las lecturas.
- Conectar el ESP32 a la red Wi-Fi usando las siguientes credenciales:
  
  ```cpp
  const char* ssid = "Nokia"; //nombre de la red
  const char* password = "paulo123"; // contraseña de la red
  ```
    Los datos del sensor se envían al servidor Flask en la dirección:

  ```cpp

    const char* serverName = "http://192.168.12.150:5000/save_sensor_data";
  ```

### 2. Cargar el código en el ESP32
  Abrir ArduinoProyecto.cpp en el IDE de Arduino y carga el código en el ESP32.
  Asegúrarse de tener instaladas las bibliotecas (Adafruit_GFX, Adafruit_SSD1306, WiFi, HTTPClient).

### 3. Configurar la base de datos PostgreSQL

  Ejecutar el script TablasPosgreSQL.sql para crear las tablas necesarias en PostgreSQL e inicializar los datos desde     uv_index_lima.csv.

### 4. Ejecutar la aplicación Flask

 - Instalar las dependencias (Flask y SQLAlchemy).
 - Verificar que la URI de la base de datos en app.py sea correcta:
   
   ```python
     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/IOT'
    ```

 - Ejecutar la aplicación Flask con:

    ```bash
        python app.py
    ```
   
## Tópicos de Cloud

### Tópico 1: Procesamiento en tiempo real con Dataflow

Google Cloud Dataflow permite el procesamiento masivo de datos en paralelo, lo que reduce la latencia en el pipeline. El servicio ajusta automáticamente los recursos según la cantidad de datos que se está procesando, garantizando eficiencia y minimización de costos. Con esta tecnología, los datos de radiación ultravioleta se procesan casi instantáneamente después de ser recibidos, asegurando la calidad de la información para su análisis y predicción.

### Tópico 2: Monitoreo y observabilidad con Cloud Monitoring y Logging

Cloud Monitoring y Logging ofrecen visibilidad en tiempo real sobre el rendimiento del sistema. Se configuran alertas basadas en umbrales predefinidos, lo que permite una detección temprana de problemas en el pipeline. Además, Cloud Logging centraliza todos los logs de los servicios, lo que facilita la depuración y análisis de errores, asegurando que el sistema opere de manera óptima.

## Referencias

- [Building the analytics lakehouse on Google Cloud ](https://services.google.com/fh/files/emails/google-cloud-analytics-lakehouse_.pdf?utm_source=cgc-blog&utm_medium=blog&utm_campaign=NA&utm_content=blog-referral&utm_term=-)
