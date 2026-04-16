#include <Arduino_RouterBridge.h> // For monitor here

int sensorPin = A0;   // select the input pin for the potentiometer

int sensorValue = 0;  // variable to store the value coming from the sensor
int ADCResolution = 14;
float voltage = 0.0;

void setup() {
  Monitor.begin();
  analogReadResolution(ADCResolution);
  analogReference(AR_INTERNAL1V5);
}

void loop() {
  // read the value from the sensor:
  sensorValue = analogRead(sensorPin);
  voltage = sensorValue * 1.5 / ((1 << ADCResolution) - 1);

  Monitor.print("ADC = ");
  Monitor.print(sensorValue);
  Monitor.print(" | V = ");
  Monitor.println(voltage, 4); // 4 decimal values
  
  delay(100);
}