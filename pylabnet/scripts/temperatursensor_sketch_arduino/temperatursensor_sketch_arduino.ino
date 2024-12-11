#define NUM_SAMPLES 1000
#define IGNORE_FIRST 10

void setup() {
  // Set the analog resolution to 12 bits (0-4095)
  analogReadResolution(12);

  // Initialize serial communication at 9600 bits per second
  Serial.begin(9600);
}

void loop() {
  unsigned long sumA0 = 0, sumA1 = 0, sumA2 = 0, sumA11 = 0;
  int countA0 = 0, countA1 = 0, countA2 = 0, countA11 = 0;
  unsigned long startTime = millis();
  
  // Sampling for A0
  for (int i = 0; i < NUM_SAMPLES; i++) {
    int reading = analogRead(A0);
    if (i >= IGNORE_FIRST) {
      sumA0 += reading;
      countA0++;
    }
    delay(1);
  }

  // Sampling for A1
  for (int i = 0; i < NUM_SAMPLES; i++) {
    int reading = analogRead(A1);
    if (i >= IGNORE_FIRST) {
      sumA1 += reading;
      countA1++;
    }
    delay(1);
  }

  // Sampling for A2
  for (int i = 0; i < NUM_SAMPLES; i++) {
    int reading = analogRead(A2);
    if (i >= IGNORE_FIRST) {
      sumA2 += reading;
      countA2++;
    }
    delay(1);
  }

  // Sampling for A11
  for (int i = 0; i < NUM_SAMPLES; i++) {
    int reading = analogRead(A11);
    if (i >= IGNORE_FIRST) {
      sumA11 += reading;
      countA11++;
    }
    delay(1);
  }

  // Calculate averages
  float averageA0 = static_cast<float>(sumA0) / countA0;
  float averageA1 = static_cast<float>(sumA1) / countA1;
  float averageA2 = static_cast<float>(sumA2) / countA2;
  float averageA11 = static_cast<float>(sumA11) / countA11;

  // Print the averages separated by semicolons and terminate with a newline
  Serial.print(averageA0);
  Serial.print(";");
  Serial.print(averageA1);
  Serial.print(";");
  Serial.print(averageA2);
  Serial.print(";");
  Serial.print(averageA11);
  Serial.println(); // Terminate with a newline

  // Wait before repeating the loop
  delay(1000);  // Wait 1 second before starting again
}