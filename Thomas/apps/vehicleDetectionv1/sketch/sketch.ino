void setup() {
  pinMode(LED4_R, OUTPUT);
  pinMode(LED4_G, OUTPUT);
  pinMode(LED4_B, OUTPUT);
}

void loop() {
  digitalWrite(LED4_R, LOW);
  digitalWrite(LED4_G, LOW);
  digitalWrite(LED4_B, LOW);
  delay(1000);

  digitalWrite(LED4_R, HIGH);
  digitalWrite(LED4_G, HIGH);
  digitalWrite(LED4_B, HIGH);
  delay(1000);
}
