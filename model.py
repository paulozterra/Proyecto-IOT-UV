import pandas as pd
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
import joblib

engine = create_engine('postgresql://postgres:123@localhost:5432/IOT')

query = "SELECT indiceuv, hora, dia, diasemana FROM indice_uv_lima"
df = pd.read_sql(query, engine)

df['hora'] = pd.to_datetime(df['hora'], format='%H:%M:%S').dt.time
df['dia'] = pd.to_datetime(df['dia'])
df = df[df['hora'].between(pd.to_datetime('09:00').time(), pd.to_datetime('16:00').time())]
df = df.sort_values(by=['dia', 'hora'])

df['dia_ordinal'] = df['dia'].apply(lambda x: x.toordinal())
df['hora_decimal'] = df['hora'].apply(lambda x: x.hour + x.minute / 60.0)

day_mapping = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
df['diasemana'] = df['diasemana'].map(day_mapping)

df = df[~((df['indiceuv'] == 0) & (df['hora_decimal'] > 9) & (df['hora_decimal'] < 16))]

X = df[['dia_ordinal', 'hora_decimal', 'diasemana']]
y = df['indiceuv']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred)}")

joblib.dump(model, 'uv_index_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
