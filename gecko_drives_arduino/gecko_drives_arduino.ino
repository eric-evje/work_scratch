#include <stdint.h>

void setup(){
	Serial.begin(9600);
	Serial.setTimeout(100);
	// pinMode(2, OUTPUT);
	pinMode(3, OUTPUT);
	pinMode(4, OUTPUT);
	pinMode(5, OUTPUT);
	pinMode(6, OUTPUT);
	pinMode(7, OUTPUT);
	pinMode(8, OUTPUT);
	pinMode(9, OUTPUT);
	pinMode(13, OUTPUT);

	digitalWrite(13, LOW);
}

void loop(){
	processIncoming();
}

void blink(){
	for (int i = 0; i < 10; i++) {
		digitalWrite(13, HIGH);
		delay(10);
		digitalWrite(13, LOW);
		delay(10);
	}
}

void processIncoming(){
	if (Serial.available() > 0) {
		// blink();
		int incoming_byte = Serial.read();
		Serial.print(incoming_byte);
		Serial.print("\n");

		if (incoming_byte == int('R')){
			blink();

			digitalWrite(6, HIGH);
			digitalWrite(7, HIGH);
			digitalWrite(8, HIGH);
			digitalWrite(9, HIGH);
			delay(100);
			digitalWrite(6, LOW);
			digitalWrite(7, LOW);
			digitalWrite(8, LOW);
			digitalWrite(9, LOW);
			Serial.print("Reset\n");
		}

		else if(incoming_byte == int('H')){
			blink();

			digitalWrite(3, HIGH);
			delay(100);
			digitalWrite(3, LOW);
			Serial.print("Homing\n");
		}

		else if(incoming_byte == int('U')){
			blink();

			digitalWrite(4, HIGH);
			delay(100);
			digitalWrite(4, LOW);
			Serial.print("Unsealing\n");
		}

		else if(incoming_byte == int('S')){
			blink();

			digitalWrite(5, HIGH);
			delay(100);
			digitalWrite(5, LOW);
			Serial.print("Sealing\n");
		}
	}	
}