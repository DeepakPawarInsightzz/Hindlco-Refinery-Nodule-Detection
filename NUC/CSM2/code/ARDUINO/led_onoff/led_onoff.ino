char serialData;
int pin1=2;
int pin2=3;

void setup(){
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
  Serial.begin(9600);
  digitalWrite(pin1, LOW);
  digitalWrite(pin2, LOW);
  }

// loop runs over and over again
void loop(){
  if(Serial.available()>0){
   
      serialData = Serial.read();
      Serial.print(serialData);
  

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
}     
