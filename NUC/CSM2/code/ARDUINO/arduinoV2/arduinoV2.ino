// relay is normally on when powered so the AC wires are to be connected in normally closed
// when a pin connected relay triggered, relay turns off

/*
  The circuit:
  - LED attached from pin 12 to ground
  - pushbutton attached to pin 2 from +5V
  - 10K resistor attached to pin 2 from ground
*/
int serialData;
int pin1=2; // for alarm
int pin2=3; // for machine

const byte buttonPin = A1;     // the number of the pushbutton pin
int buttonState = 0;         // variable for reading the pushbutton status
int val1 = 1;
int val0 = 0;

void setup(){
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
  // turning off relay
  digitalWrite(pin1, LOW);
  digitalWrite(pin2, LOW);
  Serial.begin(9600);
  }
// loop runs over and over again
void loop(){
    // read the state of the pushbutton value:
  buttonState = analogRead(buttonPin);
  Serial.println(buttonState);
  delay(100);
  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  //if (buttonState <  40) {
    // turn LED on:
   // if (millis() - time_now >= period){
    //  time_now = millis();
    //  Serial.println(val1);
   // }
 // }

    while (Serial.available())
    {
      serialData = Serial.read();
    }
    // turning off relay alarm
    if(serialData == '1'){
     digitalWrite(pin1, HIGH);
    }

    else if(serialData == '2'){
      digitalWrite(pin2, HIGH);
    }

    else if(serialData == '0'){
      digitalWrite(pin1, LOW);
      digitalWrite(pin2, LOW);
    }
}     
