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

		if (incoming_byte == "R"){
			digitalWrite(1, HIGH);
			delay(100);
			digitalWrite(1, LOW);
		}

		else if(incoming_byte == "H"){
			digitalWrite(2, HIGH);
			delay(100);
			digitalWrite(2, LOW);
		}

		else if(incoming_byte == "U"){
			digitalWrite(3, HIGH);
			delay(100);
			digitalWrite(3, LOW);
		}

		else if(incoming_byte == "S"){
			digitalWrite(4, HIGH);
			delay(100);
			digitalWrite(4, LOW);
		}
	}
		
}