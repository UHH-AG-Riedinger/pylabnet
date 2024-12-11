const int ledPin = 13; // Pin connected to the internal LED
const int pwmPin = 9;  // Set PWM pin (D9) for your signal
const int highValue = 255; // Full PWM output for a high signal
const int lowValue = 0;    // No PWM output for a low signal

void setup() {
  pinMode(ledPin, OUTPUT); // Set the internal LED pin as an output
  pinMode(pwmPin, OUTPUT); // Set the PWM pin as an output
  Serial.begin(9600);          // Start serial communication
  Serial.flush();
}

void loop() {
  if (Serial.available() > 0) {
    // Read the incoming byte
    String command = Serial.readStringUntil('\n');

    // Compare the received command
    if (command == "ON") {
      digitalWrite(ledPin, HIGH);
      analogWrite(pwmPin, highValue);
    } else if (command == "OFF") {
      digitalWrite(ledPin, LOW);
      analogWrite(pwmPin, lowValue);
    }
  } 
}