CREATE TABLE sensor_value (
    id INTEGER PRIMARY KEY,
    sensor_value DOUBLE PRECISION,
    date DATE,
    time TIME WITHOUT TIME ZONE,
    uv_index INTEGER
);

CREATE TABLE last_ten_values (
    id INTEGER PRIMARY KEY,
    position INTEGER,
    uv_index INTEGER,
    sensor_value DOUBLE PRECISION
);

CREATE TABLE indice_uv_lima (
    id SERIAL PRIMARY KEY,
    indiceuv INTEGER,
    hora TIME WITHOUT TIME ZONE,
    dia DATE,
    diasemana VARCHAR(10)
);

COPY indice_uv_lima(indiceuv, hora, dia, diasemana)
FROM '/uv_index_lima.csv'
DELIMITER ','
CSV HEADER;

