// relay is normally on when powered so the AC wires are to be connected in normally closed
// when a pin connected relay triggered, relay turns off

/*
  The circuit:
  - LED attached from pin 12 to ground
  - pushbutton attached to pin 2 from +5V
  - 10K resistor attached to pin 2 from ground
*/
int serialData;
int pin1=12; // for alarm
int pin2=11; // for machine

const byte buttonPin = A1;     // the number of the pushbutton pin
int buttonState = 0;         // variable for reading the pushbutton status
int val1 = 1;
int val0 = 0;

unsigned long time_now = 0;
int period = 100;

unsigned long time_now_alarm = 0;
int period_alarm = 10000;
int alarm_var = 0;

unsigned long time_now_machine = 0;
int period_machine = 10000;
int machine_var = 0;

void setup(){
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
  // turning off relay
  digitalWrite(pin1, HIGH);
  digitalWrite(pin2, HIGH);
  Serial.begin(9600);
  }
// loop runs over and over again
void loop(){
    // read the state of the pushbutton value:
  buttonState = analogRead(buttonPin);
  //Serial.println(val1);
  //delay(100);
  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState <  50) {
    // turn LED on:
    if (millis() - time_now >= period){
      time_now = millis();
      Serial.println(val1);
    }
  }
 /* timer for alarm
  if (digitalRead(pin1) == LOW){
      if (millis() - time_now_alarm >= period_alarm){
        time_now_alarm = millis();
        digitalWrite(pin1, HIGH);
        alarm_var = 1;
      }
  }
  //timer for machine
  if (digitalRead(pin2) == LOW){
      if (millis() - time_now_machine >= period_machine){
        time_now_machine = millis();
        digitalWrite(pin2, HIGH);
        machine_var = 1;
      }
  }*/

    while (Serial.available())
    {
      serialData = Serial.read();
    }
    // turning off relay alarm
    if(serialData == '0'){
     alarm_var = 0;
     alarm_var = 0; 
     digitalWrite(pin1, HIGH);
     alarm_var = 0;
     alarm_var = 0;
    }

    // turning on relay
    else if(serialData == '1' and alarm_var == 0){
      digitalWrite(pin1, LOW);
    //else if(serialData == '0' and alarm_var == 0){
      digitalWrite(pin1, HIGH); 
    //else if(serialData == '1' and alarm_var == 0){
      digitalWrite(pin1, LOW);    
      
      
    }

    //turning off relay machine
    else if(serialData == '2'){
      machine_var = 0;
      machine_var = 0;
      digitalWrite(pin2, HIGH);
      machine_var = 0;
      machine_var = 0;
    }

    // turning on relay machine
    else if(serialData == '3' and machine_var == 0){
    digitalWrite(pin2, LOW);
    }
    // turning on relay machine alarm
    else if(serialData == '5' and machine_var == 0 and alarm_var == 0){
    digitalWrite(pin1, LOW);
    digitalWrite(pin2, LOW);
    }

}     
