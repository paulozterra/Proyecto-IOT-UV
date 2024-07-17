#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

const char* ssid = "Nokia";
const char* password = "paulo123";

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

const int sensorPin = 34; 

const char* serverName = "http://192.168.12.150:5000/save_sensor_data"; 

void setup() {
  Serial.begin(115200);
  delay(10);

  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.println("Dirección IP:");
  Serial.println(WiFi.localIP());

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("No se encuentra la pantalla SSD1306"));
    for(;;);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Hola, mundo!");
  display.display();
}


void loop() {
  int sensorValue = analogRead(sensorPin);
  Serial.println(sensorValue);

  int uv_index = map(sensorValue, 0, 4095, 0, 15);
  char sensorValueStr[10];
  dtostrf(sensorValue, 1, 2, sensorValueStr);
  char uvIndexStr[10];
  dtostrf(uv_index, 1, 2, uvIndexStr);

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Valor del sensor:");
  display.setCursor(0, 10);
  display.print(sensorValueStr);
  display.println(" (ADC)");
  display.setCursor(0, 30);
  display.println("Indice UV:");
  display.setCursor(0, 40);
  display.println(uvIndexStr);
  display.display();

  if(WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;

    String serverPath = serverName + String("?sensor_value=") + sensorValueStr + "&uv_index=" + uvIndexStr;

    http.begin(client, serverPath); 

    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
    } else {
      Serial.print("Error en la conexión HTTP: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("Error en la conexión WiFi");
  }

  delay(1000);  
}
