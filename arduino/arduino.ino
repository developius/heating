#include <SPI.h>
#include "RF24.h"

RF24 radio(9,10);
const uint64_t pipes[2] = { 0xF0F0F0F0E2LL, 0xF0F0F0F0E1LL };
//const uint64_t pipes[2] = { 0xf0f0f0f0e2LL, 0xf0f0f0f0e1LL };
char payload[32];
const int relay = 8;
const int statusLED = 7;
unsigned char relay_status;
String node;
int threshold = 16;
String device_status; // not int as will contain 0,1 & "-"
int temp; // testing purposes

void setup(void){
  pinMode(relay, OUTPUT);
  pinMode(statusLED, OUTPUT);
  digitalWrite(statusLED, LOW);
  Serial.begin(57600);
  radio.begin();
  radio.enableDynamicPayloads();
  radio.setDataRate(RF24_1MBPS);
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(76);
  radio.setRetries(15,15);
  radio.openWritingPipe(pipes[0]); 
  radio.openReadingPipe(1,pipes[1]); 
  radio.startListening();
  Serial.println("\nReady!\n");
  delay(1000);
}

void send_mode(){
  radio.openWritingPipe(pipes[1]);
  radio.openReadingPipe(0,pipes[0]);
//  radio.stopListening();
}

void recv_mode(){
  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1,pipes[1]);
//  radio.startListening();
}

void loop(void){
  while (radio.available()){
    digitalWrite(statusLED, HIGH);
//    unsigned char length = radio.getDynamicPayloadSize();
    int length = radio.getDynamicPayloadSize();
    bool done = false;
    while (!done){
       done = radio.read(payload, length);
       payload[length] = 0;
       node = String(payload[0]);// + String(payload[1]);
       if (node == "0"){
         if ((String(payload[1]) + String(payload[2]) + String(payload[3]) + String(payload[4])) == "temp"){
             temp = random(0,30);
             Serial.print("Server asked for temp... sending...");
             radio.stopListening();
             while (!radio.write(&temp,sizeof(temp))){
           //    Serial.print("\nFailed");
             }
             Serial.print("Sent\n");
             radio.startListening();
           }
         else {
           threshold = (SMtring(payload[1]) + String(payload[2])).toInt();
           device_status = String(payload[3]);
           // check for device_status
           if (device_status == "1"){
             relay_status = HIGH;
           }
           if (device_status == "0") {
             relay_status = LOW;
           }
           Serial.print("Node: " + node + "\n");
           Serial.print("Threshold: " + String(threshold) + "\n");
           Serial.print("device_status: " + device_status + "\n");
         }
       }
       digitalWrite(statusLED, LOW);
    }
  }
  // check if we are too cold
  if (temp < threshold && device_status == "1"){
    relay_status = HIGH;
    Serial.print("Too cold!\n\r");
  }
  else if (temp >= threshold && device_status == "1") { // we are too hot
    relay_status = LOW;
    Serial.print("Too hot!\n\r");
  }
  digitalWrite(relay, relay_status);
  delay(250);
}
