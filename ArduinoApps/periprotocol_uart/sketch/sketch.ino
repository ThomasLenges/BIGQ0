=== Read and send back read data ===
String incoming = "";

void setup() {
  // Initialize the hardware UART at 115200 baud
  Serial.begin(115200);
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      // Echo the buffered message and add a newline
      Serial.println(incoming);

      // Clear for the next message
      incoming = "";
    } else {
      incoming += c;
    }
  }
}