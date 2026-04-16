const int analogInPin = A0;  // Analog input pin that the potentiometer is attached to
const int pwmOutPin = D3;    // PWM output pin

int sensorValue = 0;  // value read from the pot
int outputValue = 0;  // value output to the PWM (analog out)

void setup() {
  // Define the PWM output resolution
  analogWriteResolution(10);  // 0 - 1023 -> 0 - 100% duty-cycle
  analogReadResolution(14);   // 0 - 16383
}

void loop() {
  // read the analog in value:
  sensorValue = analogRead(analogInPin);
  // map it to the range of the analog out:
  outputValue = map(sensorValue, 0, 16383, 0, 1024);
  // change the analog out value:
  analogWrite(pwmOutPin, outputValue);

  // wait 2 milliseconds before the next loop for the ADC
  // to settle after the last reading:
  delay(2);
}