const float freq = 60.0f;
const int   N    = 256;     // 256 samples/period
const uint32_t Ts_us = (uint32_t)llroundf(1e6f / (freq * N)); // Time distance between two points 
// (60*256): nb values to send per second with such sampling to get goal frequence
// *1e6f to get in microseconds
// llroundf rounds a float to a long long (closest value)

uint16_t lut[N]; // store the sine wave here

void setup() {
  analogWriteResolution(12);

  for (int i = 0; i < N; ++i){
      lut[i] = 2048 + (1000.0 * sin(2 * PI * i / N)); // sin(x) x from 0 to 2 pi
  } // As we set resolution to 12 bits [0; 4095] with set sin middle to 2048 and then add an aplitude to +-1000 [1048;3048]

}

void loop() {
  static uint32_t t_next = micros(); // Gets time since start [ms]. Static so keeps timing at each loop iteration
  for (int i = 0; i < N; ++i) {
    analogWrite(DAC0, lut[i]);  // output the sine wave values
    t_next += Ts_us;
    while ((int32_t)(micros() - t_next) < 0) { /* spin */ } // Stuck in here until Ts_us passed (new point in sinusoid)
  }
}