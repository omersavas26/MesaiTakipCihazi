int sinyal = 7, buzzer = 8, role = 9;

void cal()
{
  digitalWrite(role, HIGH);
  
  int t = 500;
  for(int i = 0; i< 5; i++)
  {
    tone(buzzer, t);
    delay(100);
    t += 40;
    noTone(buzzer);
    delay(5);
  }
  
  noTone(buzzer);
  
  digitalWrite(role, LOW);
  /*delay(500);
  digitalWrite(role, HIGH);
  delay(500);
  digitalWrite(role, LOW);*/
  
}

void setup() {
  delay(60000);
  pinMode(sinyal, INPUT);
  pinMode(buzzer, OUTPUT);
  
  pinMode(role, OUTPUT);
  digitalWrite(role, LOW);
}

void loop() 
{
  if(digitalRead(sinyal))
  {
    cal();
  }
}
