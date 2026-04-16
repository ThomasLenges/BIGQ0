#include <Arduino_RouterBridge.h>

BridgeTCPClient<> client(Bridge);

void setup() {
  bool okBridge = Bridge.begin();
  bool okMon = Monitor.begin();

  delay(1000);

  Monitor.print("Bridge.begin(): ");
  Monitor.println(okBridge ? "OK" : "FAIL");
  Monitor.print("Monitor.begin(): ");
  Monitor.println(okMon ? "OK" : "FAIL");
}

void loop() {
  Monitor.println("\nConnecting to time.nist.gov ...");

  if (client.connect("time.nist.gov", 13) < 0) {
    Monitor.println("Connection failed!");
    delay(5000);
    return;
  }

  Monitor.println("Connected, reading response...");
  String line;
  while (client.connected() || client.available()) {
    if (client.available()) {
      char c = client.read();
      if (c == '\n') break; // daytime sends one line
      if (c != '\r') line += c;
    }
  }

  Monitor.print("Server says: ");
  Monitor.println(line);

  client.stop();
  delay(10000);
}