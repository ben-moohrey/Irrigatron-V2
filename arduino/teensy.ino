#include <PID_v1.h>
#include <Encoder.h> 
#include <stdlib.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

//IMU stuff
uint16_t BNO055_SAMPLERATE_DELAY_MS = 250; //how often to read data from the board
uint16_t PRINT_DELAY_MS = 100; // how often to print the data
static float prevX = 0, prevY = 0, prevTheta = 0;
static unsigned long prevTime = 0;
static float vX = 0, vY = 0; // Velocity in X and Y
double DEG_2_RAD = 0.01745329251; //trig functions require radians, BNO055 outputs degrees
sensors_event_t orientationData, linearAccelData;

//test imu stuff
float tempX = 0, tempY = 0;
float posX = 0, posY = 0;
unsigned long lastTime = 0;


Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);

imu::Vector<3> accelBias;

//top left motor PIN        //top right motor PIN
int tLeftPWM_PIN      = 7;    int tRightPWM_PIN      = 4;
int tLeftForward_PIN  = 6;    int tRightForward_PIN  = 3;
int tLeftReverse_PIN  = 5;    int tRightReverse_PIN  = 2;
int tLeftEncoderA_PIN = 21;   int tRightEncoderA_PIN = 16;
int tLeftEncoderB_PIN = 22;   int tRightEncoderB_PIN = 17;

//bottom left motor PIN     //bottom right motor PIN
int bLeftPWM_PIN      = 13;   int bRightPWM_PIN      = 10;
int bLeftForward_PIN  = 15;   int bRightForward_PIN  = 9;
int bLeftReverse_PIN  = 14;   int bRightReverse_PIN  = 8;
int bLeftEncoderA_PIN = 0;    int bRightEncoderA_PIN = 11;
int bLeftEncoderB_PIN = 1;    int bRightEncoderB_PIN = 12;


//Initialize values
double tLeft_input  = 0;    double tRight_input  = 0;
double tLeft_output = 0;    double tRight_output = 0;
double tLeft_setpoint=0;    double tRight_setpoint=0;

double bLeft_input  = 0;    double bRight_input  = 0;
double bLeft_output = 0;    double bRight_output = 0;
double bLeft_setpoint=0;    double bRight_setpoint=0;

//PID parameters
//double Kp = 0.00622; //0.00822
double Kp = 0.15022; //0.01022;//Increase it to a point where the motor responds quickly enough but is not overly oscillatory or unstable.
double Ki = 0.659; // Once Kp is set for good responsiveness, increase Kd to mitigate any overshoot or oscillations introduced by Kp. This helps in smoothing out the response.
double Kd = 0.003; //Lastly, adjust Ki if there are any persistent steady-state errors. Ki should be tweaked to correct these errors without causing the motor to respond too sluggishly.

PID tLeftPID ( &tLeft_input,  &tLeft_output,  &tLeft_setpoint, Kp, Ki, Kd, DIRECT);
PID tRightPID(&tRight_input, &tRight_output, &tRight_setpoint, Kp, Ki, Kd, DIRECT);
PID bLeftPID ( &bLeft_input,  &bLeft_output,  &bLeft_setpoint, Kp, Ki, Kd, DIRECT);
PID bRightPID(&bRight_input, &bRight_output, &bRight_setpoint, Kp, Ki, Kd, DIRECT);


//Reading Speed
Encoder tLeftEncoder (tLeftEncoderA_PIN,  tLeftEncoderB_PIN);
Encoder tRightEncoder(tRightEncoderA_PIN, tRightEncoderB_PIN);
Encoder bLeftEncoder (bLeftEncoderA_PIN,  bLeftEncoderB_PIN);
Encoder bRightEncoder(bRightEncoderA_PIN, bRightEncoderB_PIN); 

//initialize speed
int tleftSpeed = 0;
int bleftSpeed = 0;
int trightSpeed = 0;
int brightSpeed = 0;
int pumpSpeed = 255;

int pumpEnable = 23;
int pumpGo = 20;

void calibrateSensors(imu::Vector<3>& accelBias) {
    imu::Vector<3> accelSum;
    for (int i = 0; i < 100; i++) {
        imu::Vector<3> accel = bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
        accelSum.x() += accel.x();
        accelSum.y() += accel.y();
        accelSum.z() += accel.z();
        delay(10);
    }
    // Compute average
    accelBias.x() = accelSum.x() / 100;
    accelBias.y() = accelSum.y() / 100;
    accelBias.z() = accelSum.z() / 100;
}





void setup(){ 

 //PinMode
 pinMode(tLeftPWM_PIN,     OUTPUT);  pinMode(tRightPWM_PIN,     OUTPUT);
 pinMode(tLeftForward_PIN, OUTPUT);  pinMode(tRightForward_PIN, OUTPUT);
 pinMode(tLeftReverse_PIN, OUTPUT);  pinMode(tRightReverse_PIN, OUTPUT);
 pinMode(tLeftEncoderA_PIN,INPUT) ;  pinMode(tRightEncoderA_PIN,INPUT);
 pinMode(tLeftEncoderB_PIN,INPUT) ;  pinMode(tRightEncoderB_PIN,INPUT);
 
 pinMode(bLeftPWM_PIN,     OUTPUT);  pinMode(bRightPWM_PIN,     OUTPUT);
 pinMode(bLeftForward_PIN, OUTPUT);  pinMode(bRightForward_PIN, OUTPUT);
 pinMode(bLeftReverse_PIN, OUTPUT);  pinMode(bRightReverse_PIN, OUTPUT);
 pinMode(bLeftEncoderA_PIN,INPUT) ;  pinMode(bRightEncoderA_PIN,INPUT);
 pinMode(bLeftEncoderB_PIN,INPUT) ;  pinMode(bRightEncoderB_PIN,INPUT);

 //Initialize PID & Encoder
 tLeftPID.SetMode(AUTOMATIC);        tRightPID.SetMode(AUTOMATIC);
 tLeftPID.SetSampleTime(50);         tRightPID.SetSampleTime(50);
 tLeftPID.SetOutputLimits(-700,700); tRightPID.SetOutputLimits(-700,700);
 tLeftEncoder.write(0);              tRightEncoder.write(0);
 
 bLeftPID.SetMode(AUTOMATIC);        bRightPID.SetMode(AUTOMATIC);
 bLeftPID.SetSampleTime(50);         bRightPID.SetSampleTime(50);
 bLeftPID.SetOutputLimits(-700,700); bRightPID.SetOutputLimits(-700,700);
 bLeftEncoder.write(0);              bRightEncoder.write(0);
 
 //pump
 pinMode(pumpEnable, OUTPUT);
 pinMode(pumpGo, OUTPUT);


 Serial.begin(115200);

  //honestly not 100% sure if needed but it broke last time i removed it
  if(!bno.begin())
   {
     /* There was a problem detecting the BNO055 ... check your connections */
     Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
     while(1);
   }

  bno.setExtCrystalUse(true);
  //for timing
  prevTime = millis();
  lastTime = millis();

  calibrateSensors(accelBias);

}


//Determine DIR and apply PWM
void applyPWM(double pwmValue,int PWMPIN, int dirPIN1, int dirPIN2){

 if (pwmValue >= 0) {
   digitalWrite(dirPIN1, HIGH);
   digitalWrite(dirPIN2, LOW);
   }

   else {
   digitalWrite(dirPIN1, LOW);
   digitalWrite(dirPIN2, HIGH);
   }
   
 analogWrite(PWMPIN,abs(pwmValue));
}



void readSpeed(){ 
 if(Serial.available()>0){
   String string_input = Serial.readStringUntil('\n');

   if (string_input == "p") {
     pumpin();
   }

   else if (string_input == "x") {
     notPumpin();
   }

   else if (string_input == "z"){
     calibration();
   }

   else{
     tLeft_setpoint = (double)string_input.substring(0, string_input.indexOf(';')).toFloat();
       string_input = string_input.substring(string_input.indexOf(';') + 1);
       
     bLeft_setpoint = (double)string_input.substring(0, string_input.indexOf(';')).toFloat();
       string_input = string_input.substring(string_input.indexOf(';') + 1);
       
     tRight_setpoint = (double)string_input.substring(0, string_input.indexOf(';')).toFloat();
       string_input = string_input.substring(string_input.indexOf(';') + 1);

     //bRight_setpoint = (double)string_input.toFloat();
     bRight_setpoint = (double)string_input.substring(0, string_input.indexOf(';')).toFloat();
   }
 }
}

void pumpin(){
 // Serial.println("pumpin!");
 analogWrite(pumpEnable, 255);
 digitalWrite(pumpGo, HIGH);
}

void notPumpin(){
 // Serial.println("NOT pumpin!");
 analogWrite(pumpEnable, 0);
 digitalWrite(pumpGo, LOW);
}

/*
//do not delete this one
void IMU() {
  // Get the current time
  unsigned long currentTime = millis();

  // Check if the sample rate delay has passed
  if (currentTime - prevTime >= BNO055_SAMPLERATE_DELAY_MS) {
    float deltaTime = (currentTime - prevTime) / 1000.0f; // deltaTime in seconds

    // Read IMU sensor data
    sensors_event_t linearAccelData, gyroData, orientationData;
    bno.getEvent(&linearAccelData, Adafruit_BNO055::VECTOR_LINEARACCEL);
    bno.getEvent(&gyroData, Adafruit_BNO055::VECTOR_GYROSCOPE);
    bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);

    // Gyroscope data in radians per second
    float gX = gyroData.gyro.x * DEG_2_RAD;
    float gY = gyroData.gyro.y * DEG_2_RAD;
    float gZ = gyroData.gyro.z * DEG_2_RAD; // Rotation around the Z-axis

    // Update theta based on z-axis gyroscope
    float deltaTheta = gZ * deltaTime; // Change in orientation since last loop iteration
    prevTheta += deltaTheta; // Accumulate the total rotation around z-axis

    // Update velocities based on acceleration
    vX += linearAccelData.acceleration.x * deltaTime; // m/s
    vY += linearAccelData.acceleration.y * deltaTime; // m/s

    // Convert velocity to displacement
    float deltaX = vX * deltaTime; // Change in x position since last loop iteration
    float deltaY = vY * deltaTime; // Change in y position since last loop iteration

    // Update the global x and y positions with the calculated delta positions
    prevX += deltaX;
    prevY += deltaY;

    // Update prevTime for the next iteration
    prevTime = currentTime;

    // Print the data for debugging purposes
    Serial.print("deltaX: "); Serial.print(deltaX);
    Serial.print(" deltaY: "); Serial.print(deltaY);
    Serial.print(" deltaTheta: "); Serial.print(deltaTheta);
    Serial.print(" deltaTime: "); Serial.println(deltaTime);
  }
  // Else, do nothing until the sample rate delay has passed
}
*/

void calibration(){
  uint8_t system, gyro, accel, mag = 0;
  Serial.println("---------------Calibration DATA---------------");
  bno.getCalibration(&system, &gyro, &accel, &mag);
  Serial.print("CALIBRATION: Sys=");
  Serial.print(system, DEC);
  Serial.print(" Gyro=");
  Serial.print(gyro, DEC);
  Serial.print(" Accel=");
  Serial.print(accel, DEC);
  Serial.print(" Mag=");
  Serial.println(mag, DEC);

  /*
  Accelerometer Calibration:
  Place the device on a flat surface and keep it still in different orientations. 
  Typically, six orientations are used: laying flat on each side and turning it 180 degrees on each axis. 
  Wait a few seconds in each position.
  
  Magnetometer Calibration:
  Move the sensor in a figure-eight motion. This movement should be slow and steady, 
  covering various orientations and angles. This helps the sensor understand the surrounding magnetic field better.
  
  Gyroscope Calibration:
  This appears to be calibrated already, but it generally involves keeping the sensor still for a few seconds. 
  Gyroscopes are sensitive to rotations, so ensure there are no movements during this phase.
  
  System Calibration:
  System calibration usually benefits from having all the other sensors calibrated. 
  Move the sensor through various static and dynamic states as required by the other three sensors.
  */
  
}


void testIMU() {
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    imu::Vector<3> accel = bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);

    // Correct the acceleration reading by subtracting the bias
    accel.x() -= accelBias.x();
    accel.y() -= accelBias.y();

    unsigned long currentTime = millis();
    float deltaTime = (currentTime - lastTime) / 1000.0f;  // Time in seconds
    lastTime = currentTime;

    // Update velocities
    float newVx = vX + accel.x() * deltaTime;
    float newVy = vY + accel.y() * deltaTime;

    // Calculate delta positions
    float deltaX = 0.5 * (vX + newVx) * deltaTime;  // Trapezoidal integration
    float deltaY = 0.5 * (vY + newVy) * deltaTime;  // Trapezoidal integration

    // Update velocities for next iteration
    vX = newVx;
    vY = newVy;

    float yaw = euler.x();  // Yaw from Euler angles

    // Print the calculated deltas and yaw
    Serial.print("Yaw: "); Serial.print(yaw);
    Serial.print(" Δx: "); Serial.print(deltaX);
    Serial.print(" Δy: "); Serial.println(deltaY);

    delay(50);
}





void loop(){ 
  
  
 testIMU();
  //calibration();
 readSpeed();

 tLeft_input = tLeftEncoder.read();
 tLeftPID.Compute();
 applyPWM(tLeft_output,  tLeftPWM_PIN,  tLeftForward_PIN,  tLeftReverse_PIN);
 
 tRight_input = -tRightEncoder.read();
 tRightPID.Compute();
 applyPWM(tRight_output, tRightPWM_PIN, tRightForward_PIN, tRightReverse_PIN);
 
 bLeft_input = bLeftEncoder.read();
 bLeftPID.Compute();
 applyPWM(bLeft_output,  bLeftPWM_PIN,  bLeftForward_PIN,  bLeftReverse_PIN);

 bRight_input = -bRightEncoder.read();
 bRightPID.Compute();
 applyPWM(bRight_output, bRightPWM_PIN, bRightForward_PIN, bRightReverse_PIN);

 tLeftEncoder.write(0);tRightEncoder.write(0);bLeftEncoder.write(0);bRightEncoder.write(0);
 
 delay(50); 
}
