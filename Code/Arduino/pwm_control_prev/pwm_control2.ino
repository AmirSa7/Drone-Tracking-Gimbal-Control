
#include <Scheduler.h>

#define VERT_DIR_PIN 8
#define HORZ_DIR_PIN 7

#define VERT_OUT_PIN 10
#define HORZ_OUT_PIN 9

int vert_dir;
int horz_dir;

int w_horz;		// Speed in steps per second
int w_vert;		// Expected range is 0-300

int horz_delay;
int vert_delay;
int horz_T;
int vert_T;
bool horz_up;
bool vert_up;

int prev_horz_dir;
int prev_vert_dir;

int pulse = 100; //Pulse length in microseconds

void setup() {
	Serial.begin(9600);
	pinMode(VERT_DIR_PIN, OUTPUT);
	pinMode(HORZ_DIR_PIN, OUTPUT);
	pinMode(VERT_OUT_PIN, OUTPUT);
	pinMode(HORZ_OUT_PIN, OUTPUT);

  digitalWrite(HORZ_DIR_PIN, 0);
  digitalWrite(VERT_DIR_PIN, 0);

  w_horz = 0;
  w_vert = 0;

  prev_horz_dir = 0;
  prev_vert_dir = 0;

  horz_delay = 0;
  vert_delay = 0;

  pulse = 100; //Pulse length in microseconds

  horz_up = false;
  vert_up = false;

	Scheduler.startLoop(set_speed_loop);
}

void set_speed_loop()
{
	int min_delay;

	if (horz_delay == 0) {
		if (horz_up) {
			digitalWrite(HORZ_OUT_PIN, 0);
			horz_delay = (horz_T - pulse);
			horz_up = false;
		} else {
			if (w_horz != 0) {
				horz_T = 100000/w_horz;
       if (prev_horz_dir != horz_dir) {
				  digitalWrite(HORZ_DIR_PIN, horz_dir);
				  delayMicroseconds(1);
          prev_horz_dir = horz_dir;
       }
				digitalWrite(HORZ_OUT_PIN, 1);
				horz_delay = pulse;
				horz_up = true;
			} else {
        horz_delay = 200;
			}
		}
	}
	if (vert_delay == 0) {
		if (vert_up) {
			digitalWrite(VERT_OUT_PIN, 0);
			vert_delay = (vert_T - pulse);
			vert_up = false;
		} else {
			if (w_vert != 0) {
				vert_T = 100000/w_vert;
        if (prev_vert_dir != vert_dir) {
				  digitalWrite(VERT_DIR_PIN, vert_dir);
				  delayMicroseconds(1);
          prev_vert_dir = vert_dir;
        }
				digitalWrite(VERT_OUT_PIN, 1);
				vert_delay = pulse;
				vert_up = true;
			} else {
        vert_delay = 200;
			}
		}
	}

	min_delay = min(vert_delay, horz_delay);

  delayMicroseconds(min_delay);
	horz_delay -= min_delay;
	vert_delay -= min_delay;

	yield();
}

void read_speed(int* w, int* dir, bool flip)
{
	*w = Serial.read();
	if (*w >= 0 && *w <= 127)
			*dir = 1;
	else {
			*w = 256 - *w;
			*dir = 0;
	}
	if(flip)
		*dir = !(*dir);
}

void loop()
{
	while(!Serial.available()) yield();
	read_speed(&w_horz, &horz_dir, false);

  Serial.write(w_horz);

  while(!Serial.available()) yield();
	read_speed(&w_vert, &vert_dir, false);

  yield();
}
