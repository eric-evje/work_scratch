#include <stdint.h>

void setup(){
	Serial.begin(9600);
	pinMode(1, OUTPUT);
	pinMode(2, OUTPUT);
	pinMode(3, OUTPUT);
	pinMode(4, OUTPUT);
}

void loop(){
	processIncoming();
}

void processIncoming(){
	if (Serial.available() > 0) {
		int incoming_byte = Serial.read();
		Serial.print(incoming_byte);
		Serial.print("\n");

		if (incoming_byte == "R\n"){
			digitalWrite(1, HIGH);
			delay(100);
			digitalWrite(1, LOW);
			Serial.print("Got an R");
			Serial.print("\n");
		}

		else if(incoming_byte == "H\n"){
			digitalWrite(2, HIGH);
			delay(100);
			digitalWrite(2, LOW);
			Serial.print("Got an H");
			Serial.print("\n");
		}

		else if(incoming_byte == "U\n"){
			digitalWrite(3, HIGH);
			delay(100);
			digitalWrite(3, LOW);
			Serial.print("Got a U");
			Serial.print("\n");
		}

		else if(incoming_byte == "S\n"){
			digitalWrite(4, HIGH);
			delay(100);
			digitalWrite(4, LOW);
			Serial.print("Got an S");
			Serial.print("\n");
		}
	}
		
}