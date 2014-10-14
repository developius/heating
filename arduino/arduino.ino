#include <SPI.h>
#include "RF24.h"
#include <OneWire.h>
#include <DallasTemperature.h>

#define ONE_WIRE_BUS 3
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
RF24 radio(9,10);
const uint64_t pipes[2] = { 
  0xF0F0F0F0E2LL, 0xF0F0F0F0E1LL };
//const uint64_t pipes[2] = { 0xf0f0f0f0e2LL, 0xf0f0f0f0e1LL };
char payload[32];
const int relay = 8;
const int statusLED = 7;
unsigned char relay_status;
String node;
int threshold = 16;
String device_status; // not int as will contain 0,1 & "-"
int temp;

void setup(void){
  sensors.begin();
  pinMode(relay, OUTPUT);
  pinMode(statusLED, OUTPUT);
  digitalWrite(statusLED, LOW);
  Serial.begin(57600);
  radio.begin();
  radio.enableDynamicPayloads();
  radio.setDataRate(RF24_250KBPS);
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(76);
  radio.setRetries(15,15);
  radio.openWritingPipe(pipes[0]); 
  radio.openReadingPipe(1,pipes[1]);
  radio.startListening();
  Serial.println("\nReady!\n");
  delay(1000);
}

void loop(void){
  radio.startListening();
  sensors.requestTemperatures();
  temp = sensors.getTempCByIndex(0);
  while (radio.available()){
    digitalWrite(statusLED, HIGH);
    int length = radio.getDynamicPayloadSize();
    bool done = false;
    while (!done){
      done = radio.read(payload, length);
      payload[length] = 0;
      node = String(payload[0]);// + String(payload[1]);
      if (node == "0"){
        if ((String(payload[1]) + String(payload[2]) + String(payload[3]) + String(payload[4])) == "temp"){
          Serial.print("Server asked for temp... ");
          radio.stopListening();
          bool timeout = false;
          unsigned long started_waiting_at = millis();
          while (!radio.write(&temp,sizeof(temp)) && !timeout){
            if (millis() - started_waiting_at > 5000 ){
              timeout = true;
            }
          }
          if (timeout){
            Serial.print("failed\n");
          }
          else {
            Serial.print("sent\n");
          }
        }
        else {
          threshold = (String(payload[1]) + String(payload[2])).toInt();
          device_status = String(payload[3]);
          Serial.print("Node: " + node + "\n");
          Serial.print("Threshold: " + String(threshold) + "\n");
          Serial.print("device_status: " + device_status + "\n");
          Serial.print("Temperature: ");
          Serial.print(sensors.getTempCByIndex(0));
          Serial.print("\n");
        }
        digitalWrite(statusLED, LOW);
      }
    }
  }
  // set the relay
  if (temp < threshold && device_status == "1"){
    relay_status = HIGH;
  }
  if (device_status == "0"){
    relay_status = LOW;
  }
  else if (temp >= threshold && device_status == "1") { // we are too hot
    relay_status = LOW;
  }
  digitalWrite(relay, relay_status);
  delay(250);
}
