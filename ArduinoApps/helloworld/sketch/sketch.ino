void setup() {
  pinMode(LED3_R, OUTPUT);
  pinMode(LED3_G, OUTPUT);
  pinMode(LED3_B, OUTPUT);
}

void loop() {
  digitalWrite(LED3_R, LOW);
  digitalWrite(LED3_G, LOW);
  digitalWrite(LED3_B, LOW);
  delay(1000);

  digitalWrite(LED3_R, HIGH);
  digitalWrite(LED3_G, HIGH);
  digitalWrite(LED3_B, HIGH);
  delay(1000);
}
