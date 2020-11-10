int sinyal = 7, buzzer = 8, role = 9;

void(* resetFunc) (void) = 0;//declare reset function at address 0

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
  
}

void setup() 
{
  pinMode(13, OUTPUT);

  Serial.begin(9600);
  
  int i = 0;
  for(i = 0; i < 60; i++)
  {
    digitalWrite(13, HIGH);
    delay(500);
    digitalWrite(13, LOW);
    delay(500);

    Serial.println(i);
  }
  
  pinMode(sinyal, INPUT);
  pinMode(buzzer, OUTPUT);
  
  pinMode(role, OUTPUT);
  digitalWrite(role, LOW);  
}

void loop() 
{
  int s = (int)(millis() / 1000);
  s = s / 60;//dk
  
  if(s > 0 && s % 400 == 0) 
  {
    Serial.println("reset");
    resetFunc();
  }
  
  if(digitalRead(sinyal))
  {
    cal();
  }
}
