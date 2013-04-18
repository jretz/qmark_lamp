#include <CapSense.h>

#include "notes.h"

/*
Normally, an ATtiny is used to control things. If an Arduino is used instead, then we can
also control things via serial. This requires slightly different wiring as pins 0 and 1,
which are used to control the light and sound from an ATtiny are the serial lines on an
Arduino and we want to have serial communications running. So the light should be moved
from pin 0 to pin 5 and sound should be moved from pin 1 to pin 6. Then change the
following #define to true and serial control will be enabled. Connect the Arduino to a
computer via USB, figure out the serial port to be used (the same one you use to program
the Arduino), then open that serial port at 9600,8,n,1 and send the one letter commands
defined below. The single letters are all you send (no line-endings or anything else) and
they are mnemonics: Dark, Light, Coin, One-up, and Pause. For example, to turn the light
on for the duration of the coin sound and then right back off, send LCD. To do that three
times with a 1/4 second pause between each, send LCDPPPPPLCDPPPPPLCD.
*/
#define SERIAL_CONTROL_ENABLED true

#if SERIAL_CONTROL_ENABLED
  #define COMMAND_LIGHT_OFF 'D'
  #define COMMAND_LIGHT_ON 'L'
  #define COMMAND_SOUND_COIN 'C'
  #define COMMAND_SOUND_ONE_UP 'O'
  #define COMMAND_PAUSE 'P'

  #define SPEAKER_PIN 6
  #define LIGHT_PIN 5
#else
  #define SPEAKER_PIN 1
  #define LIGHT_PIN 0
#endif
#define CAP_SENSOR_SEND_PIN 3
#define CAP_SENSOR_RECEIVE_PIN 4

int threshold = 150;
unsigned int pressCount = 0;

int coin_sound_num_notes = 2;
int coin_sound_notes[] = {NOTE_D6, NOTE_G6};
int coin_sound_note_durations[] = {16, 2};

int oneup_sound_num_notes = 6;
int oneup_sound_notes[] = {NOTE_E6, NOTE_G6, NOTE_E7, NOTE_C7, NOTE_D7, NOTE_G7};
int oneup_sound_note_durations[] = {8, 8, 8, 8, 8, 8};

CapSense cs_4_2 = CapSense(CAP_SENSOR_SEND_PIN, CAP_SENSOR_RECEIVE_PIN);

void setup() {
  #if SERIAL_CONTROL_ENABLED
    Serial.begin(9600);
  #endif
  pinMode(LIGHT_PIN, OUTPUT);
  digitalWrite(LIGHT_PIN, HIGH);
  delay(1000);
  digitalWrite(LIGHT_PIN, LOW);
}

void playSound(int speaker_pin, int num_notes, int notes[], int durations[]) {
  // iterate over the notes of the melody:
  for (int thisNote = 0; thisNote < num_notes; thisNote++) {
    // to calculate the note duration, take one second
    // divided by the note type.
    //e.g. quarter note = 1000 / 4, eighth note = 1000/8, etc.
    int noteDuration = 1000/durations[thisNote];
    tone(speaker_pin, notes[thisNote], noteDuration);

    // to distinguish the notes, set a minimum time between them.
    // the note's duration + 30% seems to work well:
    int pauseBetweenNotes = noteDuration * 1.30;
    delay(pauseBetweenNotes);
    // stop the tone playing:
    noTone(speaker_pin);
  }
}

boolean checkSensor() {
  #if (SERIAL_CONTROL_ENABLED == false)
    int readValue = cs_4_2.capSense(30);
    if (readValue == -2) {
      for (int i = 0; i < 2; i++) {
        digitalWrite(LIGHT_PIN, HIGH);
        delay(500);
        digitalWrite(LIGHT_PIN, LOW);
        delay(500);
      }
    }
    return readValue > threshold;
  #endif
}

void loop() {
  #if SERIAL_CONTROL_ENABLED
    int command = Serial.read();
    if (command >= 0) {
      switch(command) {
        case COMMAND_LIGHT_OFF:
          digitalWrite(LIGHT_PIN, LOW);
          break;
        case COMMAND_LIGHT_ON:
          digitalWrite(LIGHT_PIN, HIGH);
          break;
        case COMMAND_SOUND_COIN:
          playSound(SPEAKER_PIN, coin_sound_num_notes, coin_sound_notes, coin_sound_note_durations);
          break;
        case COMMAND_SOUND_ONE_UP:
          playSound(SPEAKER_PIN, oneup_sound_num_notes, oneup_sound_notes, oneup_sound_note_durations);
          break;
        case COMMAND_PAUSE:
          delay(50);
          break;
      }
    } else {
  #endif
      if (checkSensor()) {
        // the sensor was touched! increment the press count
        pressCount++;

        // toggle the light state
        if (pressCount % 2 == 0) {
          digitalWrite(LIGHT_PIN, LOW);
        } else {
          digitalWrite(LIGHT_PIN, HIGH);
        }

        // if this is the 8th touch, then play the "one up" sound
        if (pressCount % 8 == 0) {
          playSound(SPEAKER_PIN, oneup_sound_num_notes, oneup_sound_notes, oneup_sound_note_durations);
        } else {
          // always play the "coin" sound
          playSound(SPEAKER_PIN, coin_sound_num_notes, coin_sound_notes, coin_sound_note_durations);
        }
//        delay(100);
        // to "de-bounce" the touch, don't loop around again until the sensor check returns false
//        int state = LOW;
        while (checkSensor()) {
//          if (state == HIGH) {
//            state = LOW;
//          } else {
//            state = HIGH;
//          }
//          digitalWrite(LIGHT_PIN, state);
          delay(25);
        }
      }
      delay(25);
  #if SERIAL_CONTROL_ENABLED
    }
  #endif
}
