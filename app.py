from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import joblib
import pandas as pd

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123@localhost:5432/IOT'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

model = joblib.load('uv_index_model.pkl')
scaler = joblib.load('scaler.pkl')

class SensorValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uv_index = db.Column(db.Float, nullable=False)  
    sensor_value = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    time = db.Column(db.Time, default=datetime.utcnow().time)

class LastTenValues(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer, nullable=False, unique=True)
    uv_index = db.Column(db.Float, nullable=False)  
    sensor_value = db.Column(db.Float, nullable=True)

def update_last_ten_values(sensor_value, uv_index):
    for i in range(9, 0, -1):
        value = LastTenValues.query.filter_by(position=i).first()
        if value:
            value.position = i + 1
            db.session.commit()

    last_value = LastTenValues.query.filter_by(position=10).first()
    if last_value:
        db.session.delete(last_value)
        db.session.commit()

    new_value = LastTenValues(position=1, uv_index=uv_index, sensor_value=sensor_value)
    db.session.add(new_value)
    db.session.commit()

@app.route('/save_sensor_data', methods=['GET'])
def save_sensor_data():
    sensor_value = request.args.get('sensor_value')
    uv_index = request.args.get('uv_index')

    print(f"Received sensor_value: {sensor_value}, uv_index: {uv_index}")

    if sensor_value is not None and uv_index is not None:
        try:
            sensor_value = float(sensor_value)
            uv_index = float(uv_index)
            new_value = SensorValue(uv_index=uv_index, sensor_value=sensor_value)
            db.session.add(new_value)
            db.session.commit()

            update_last_ten_values(sensor_value, uv_index)

            return "Nuevo registro creado con éxito", 200
        except ValueError:
            return "Datos no válidos", 400
    else:
        return "Parámetros faltantes o no válidos", 400

@app.route('/predict_uv_index', methods=['GET'])
def predict_uv_index():
    date = request.args.get('date')
    time = request.args.get('time')

    if not date or not time:
        return "Por favor, proporciona fecha y hora", 400

    try:
        date_ordinal = pd.to_datetime(date).toordinal()
        time_decimal = pd.to_datetime(time, format='%H:%M').hour + pd.to_datetime(time, format='%H:%M').minute / 60.0
        weekday = pd.to_datetime(date).weekday()  
        hour = pd.to_datetime(time, format='%H:%M').hour
        if hour < 7 or hour >= 19:
            rounded_prediction = 0.0
        else:
            features = scaler.transform([[date_ordinal, time_decimal, weekday]]) 
            prediction = model.predict(features)
            rounded_prediction = round(prediction[0], 2)

        return jsonify({'predicted_uv_index': rounded_prediction})
    except Exception as e:
        return str(e), 400

@app.route('/get_latest_uv_index', methods=['GET'])
def get_latest_uv_index():
    latest_value = SensorValue.query.order_by(SensorValue.id.desc()).first()
    if latest_value:
        return jsonify({'sensor_value': latest_value.sensor_value, 'uv_index': latest_value.uv_index})
    else:
        return jsonify({'sensor_value': None, 'uv_index': None}), 404

@app.route('/get_last_ten_values', methods=['GET'])
def get_last_ten_values():
    values = LastTenValues.query.order_by(LastTenValues.position).all()
    result = []
    for value in values:
        result.append({
            'position': value.position,
            'sensor_value': value.sensor_value,
            'uv_index': value.uv_index
        })
    return jsonify(result)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.debug = True  
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
