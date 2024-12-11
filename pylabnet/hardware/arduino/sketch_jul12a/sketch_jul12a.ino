#include <Arduino.h>
#include <math.h>

#define PI 3.1415926535897932384626433832795

String message;
int counter = 1;
int bits = 10;
int voltage_bits = 0;
int stringCount = 0;

float minimum_Voltage = 0.535;
float maximum_Voltage = 2.75;
float full_possible_angle = 13.29;
float minimum_angle_step = 13.29/1024;

int x_default = 512;
int y_default = 812;

bool newRequest = false;

String realmessage;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(2); // If lower it does not have enough time to send all Information from Python
  pinMode(LED_BUILTIN, OUTPUT);
  analogWriteResolution(bits);
  Serial.flush();
  digitalWrite(LED_BUILTIN, LOW);
}

void checkIncomingMessage() {
  if (Serial.available()) {
    message = Serial.readStringUntil(';');
    newRequest = true;
  }
}

void loop() {
  checkIncomingMessage();
  if (newRequest) {
    newRequest = false; // Reset flag

    if (message == "DAC1") {
      message = Serial.readString();
      analogWrite(DAC1, message.toInt());
      String back_message = String("Applied value of " + message);
      Serial.write(back_message.c_str());
      message = "";
    } else if (message == "DAC0") {
      message = Serial.readString();
      analogWrite(DAC0, message.toInt());
      String back_message = String("Applied value of " + message);
      Serial.write(back_message.c_str());
      message = "";
    } else if (message == "center") {
      message = Serial.readStringUntil(';');
      x_default = message.toDouble();

      message = Serial.readString();
      y_default = message.toDouble();
      digitalWrite(LED_BUILTIN, HIGH);
      message = "";
    } else if (message == "areaStep") {
      message = Serial.readStringUntil(';');
      x_default = message.toInt();

      message = Serial.readStringUntil(';');
      y_default = message.toInt();

      message = Serial.readStringUntil(';');
      double x_steps = message.toDouble();

      message = Serial.readStringUntil(';');
      double y_steps = message.toDouble();

      message = Serial.readString();
      double times = message.toInt();

      if (times == 0) {
        times = 2147483646;
      }
      message = "";

      for (int counter = 0; counter <= times; counter++) {
        for (int i = y_default - y_steps / 2; i < y_default + y_steps / 2; i++) {
          analogWrite(DAC1, i);

          for (int k = x_default - x_steps / 2; k <= x_default + x_steps / 2; k++) {
            analogWrite(DAC0, k);
            ////delayMicroseconds(10);
          }
          delayMicroseconds(1);
          checkIncomingMessage();
          if (newRequest) {
            break;
          }
        }
        if (newRequest) {
          break;
        }
      }
    } else if (message == "pict") {
      message = Serial.readString();
      const char something[] = "0";
      analogWrite(DAC0, 1023);
      for (int k = 0; k < 300; k++) {
        for (int i = 0; i < strlen(something); i++) {
          if (something[i] == '1') {
            analogWrite(DAC0, (i % 100) * 10);
            analogWrite(DAC1, int(i / 100) * 10);
            digitalWrite(LED_BUILTIN, i % 2);
            delayMicroseconds(50);
          }
        }
        checkIncomingMessage();
        if (newRequest) {
          break;
        }
      }
      Serial.write("Done");
      message = "";
      analogWrite(DAC1, 1023);
    } else {
      // Handle unknown message
    }
    // Perform standard operations for each loop iteration
    counter++;
    counter = counter % 2;
    delayMicroseconds(1000);
    Serial.flush();
  }
}