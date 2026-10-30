#include <Arduino.h>
#include <SPI.h>
#include <MPU6500_WE.h>

const int csPin = 0;
//const int sckPin = 27;
//const int mosiPin = 26;
//const int misoPin = 1;

bool useSPI = true;    // SPI use flag

MPU6500_WE myMPU6500 = MPU6500_WE(&SPI1, csPin, useSPI);

void setup() {
  Serial.begin(115200);
  SPI1.begin();

  // If the IMU doesn't respond, keep reporting it (the GUI ignores non-numeric lines)
  if (!myMPU6500.init()) {
    while (true) {
      Serial.println("MPU6500 does not respond");
      delay(1000);
    }
  }

  delay(1000);  // let the sensor settle

  /* Choose the SPI clock speed, default is 8 MHz
     This function must be used only after init(), not before */
  myMPU6500.setSPIClockSpeed(1000000);

  //myMPU6500.autoOffsets();   // keep the board flat and still if you enable this
  //myMPU6500.setAccOffsets(0, 0, 0, 0.05, 0, 0);
  myMPU6500.setGyrOffsets(30, -121, -111);
  myMPU6500.enableGyrDLPF();
  myMPU6500.setGyrDLPF(MPU6500_DLPF_6);
  myMPU6500.setSampleRateDivider(5);
  myMPU6500.setGyrRange(MPU6500_GYRO_RANGE_250);
  myMPU6500.setAccRange(MPU6500_ACC_RANGE_2G);
  myMPU6500.enableAccDLPF(true);
  myMPU6500.setAccDLPF(MPU6500_DLPF_6);
}

void loop() {
  xyzFloat g   = myMPU6500.getGValues();
  xyzFloat gyr = myMPU6500.getGyrValues();

  // One CSV line per sample: ax,ay,az,gx,gy,gz
  Serial.print(g.x);   Serial.print(",");
  Serial.print(g.y);   Serial.print(",");
  Serial.print(g.z);   Serial.print(",");
  Serial.print(gyr.x); Serial.print(",");
  Serial.print(gyr.y); Serial.print(",");
  Serial.println(gyr.z);

  delay(20);  // ~50 samples/sec
}
