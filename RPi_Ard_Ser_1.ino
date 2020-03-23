void setup() {
  Serial.begin(9600);
  pinMode(13, OUTPUT);

}

void loop() {
  while(true){
    if(Serial.available())
    {
      int byteRead = Serial.parseInt();
      //String byteRead = Serial.readString();
      //Serial.println("Read");
      if (byteRead == 1){//"Prime"){
        Serial.write("1");//Priming");
        digitalWrite(13, HIGH);
        delay(5000);
        Serial.write("2");//Primed");
      }
      else if (byteRead == 2){//"Purge"){
        Serial.write("3");//Purging");
        digitalWrite(13, LOW);
        delay(5000);
        Serial.write("4");//Purged");
      }
      else{
      }
    }
  }
}
