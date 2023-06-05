#include <SPI.h>
#include <MFRC522.h>

// Define pins
#define gasAoPin        0
#define micDoPin        4
#define pirPin          5
#define distanceTrigPin 6
#define distanceEchoPin 7
#define buzzerPin       8
#define rdifRstPin      9          
#define rfidSsPin       10  

MFRC522 mfrc522(rfidSsPin, rdifRstPin);

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  // Set pins as input or output
  pinMode(pirPin, INPUT);
  pinMode(distanceTrigPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(distanceEchoPin, INPUT);
  pinMode(gasAoPin, INPUT);
  pinMode(micDoPin, INPUT);
  digitalWrite(buzzerPin, HIGH);

  SPI.begin();
  mfrc522.PCD_Init();
  delay(1000);
  mfrc522.PCD_DumpVersionToSerial();
}

bool cardDetected = false;
int credentials = 0;
unsigned long lastEvent = 0;

void loop() {

  // Read distance from HC-SR04 sensor
  int distance = readDistance();
  
  // Read gas level from MQ-4 sensor
  int gasLevel = readGasLevel();

  // Read sound level from microphone sensor
  int soundLevel = readSoundLevel();

  // Read motion detection
  int motion = readMotion();

  // Read RFID Connection
  if (cardDetected) {
    // Reset flag variable
    cardDetected = false;
  } else {
    // No card detected, continue scanning
    credentials = readCredentials();
    if (credentials != 0) {
      // Card detected and UID matches
      cardDetected = true;
    }
  }

  setBuzzer();

  // Output values to the serial monitor
  Serial.print("distance: ");
  Serial.println(distance);
  // Serial.println(" cm");
  
  Serial.print("pollution: ");
  Serial.println(gasLevel);
  // Serial.println(" ppm");
  
  Serial.print("sound: ");
  Serial.println(soundLevel);
  // Serial.println(" dB");

  Serial.print("motion: ");
  Serial.println(motion);

  Serial.print("access: ");
  Serial.println(credentials);
  
  // Delay before next reading
  delay(200);
}

void setBuzzer() {
  if (Serial.available() > 0) {
  char command = Serial.read();
  if (command == 'H') {
    digitalWrite(buzzerPin, HIGH);
  } else if (command == 'L') {
    digitalWrite(buzzerPin, LOW);
  }
}
}

int readDistance() {
  // Send a 10 microsecond pulse to the trigger pin
  digitalWrite(distanceTrigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(distanceTrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(distanceTrigPin, LOW);
  
  // Read the echo pulse duration in microseconds
  long duration = pulseIn(distanceEchoPin, HIGH);
  
  // Calculate the distance in centimeters
  int distance = duration / 58;
  
  return distance;
}

int readGasLevel() {
  // Read the analog voltage level on the AO pin
  int aoLevel = analogRead(gasAoPin);
  
  // Calculate the gas level in parts per million (ppm)
  int gasLevel = map(aoLevel, 0, 1023, 0, 5000);
    
  return gasLevel;
}

int readSoundLevel() {
  // Read the analog voltage level on the microphone sensor's AO pin
  int micDoLevel = digitalRead(micDoPin);
	if (micDoLevel == HIGH) {
			return 1;
		}  
  return 0;
}

int readMotion() {
  // Read pir
  int pirValue = digitalRead(pirPin);
  if (pirValue == HIGH) {
    return 1;
  }

  return 0;
}

int readCredentials() {
  // Check if there is card to read
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return 0;
  }
  // Check if UID matches expected value
  if (mfrc522.uid.uidByte[0] == 0xA3 && mfrc522.uid.uidByte[1] == 0xA3 && 
      mfrc522.uid.uidByte[2] == 0x51 && mfrc522.uid.uidByte[3] == 0x94) {
    // UID matches expected value, return 1
    return 1;
  } else {
    // UID does not match expected value
    return 2;
  }
}

