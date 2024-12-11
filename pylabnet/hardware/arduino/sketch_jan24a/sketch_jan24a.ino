void setup() {
  // Set the analog resolution to 12 bits (0-4095)
  analogReadResolution(12);

  // Initialize serial communication at 9600 bits per second
  Serial.begin(9600);

  // Optional: Wait for serial port to connect (for debugging purposes)
  while (!Serial) {
    ; // Wait for serial port to connect.
  }
}

void loop() {
  // Read the analog input values at A0, A1, A2, and A11
  int sensorValueA0 = analogRead(A0);
  int sensorValueA1 = analogRead(A1);
  int sensorValueA2 = analogRead(A2);
  int sensorValueA11 = analogRead(A11);

  // Print each sensor reading separated by semicolons and terminate with a newline
  Serial.print(sensorValueA0);
  Serial.print(";");
  Serial.print(sensorValueA1);
  Serial.print(";");
  Serial.print(sensorValueA2);
  Serial.print(";");
  Serial.print(sensorValueA11);
  Serial.println(); // Terminate with a newline

  // Optional: Add a little delay to avoid overwhelming the serial output
  delay(100);
}