#include <Arduino.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver board1 = Adafruit_PWMServoDriver(0x40);

#define SERVOMIN 125  // Minimum pulse length (0 degrees)
#define SERVOMAX 625  // Maximum pulse length (180 degrees)

int angleToPulse(int ang) {
  int pulse = map(ang, 0, 180, SERVOMIN, SERVOMAX);
  Serial.print("Angle: "); Serial.print(ang);
  Serial.print(" pulse: "); Serial.println(pulse);
  return pulse;
}

void setup() {
  Serial.begin(9600);
  Serial.println("16 channel Servo test!");
  board1.begin();
  board1.setPWMFreq(60); // Servos operate at ~60 Hz
}

void loop() {
  // Set all servos to 0 degrees
  for(int i=0; i<8; i++) {
    board1.setPWM(i, 0, angleToPulse(0));
  }
  delay(1000);
  
  // Sweep all servos from 0 to 180 degrees
  for(int angle = 0; angle < 181; angle += 10) {
    for(int i=0; i<8; i++) {
      board1.setPWM(i, 0, angleToPulse(angle));
    }
    delay(100);
  }
}