
#include <Scheduler.h>

#define VERT_DIR_PIN 7
#define HORZ_DIR_PIN 8

#define VERT_OUT_PIN 9
#define HORZ_OUT_PIN 10

enum ARD_COMMANDS {
	CMD_RESET = 101,
	CMD_SPEED_TEST_HORZ,
	CMD_SPEED_TEST_VERT,
	CMD_SET_SPEED_MOD_HORZ,
	CMD_SET_SPEED_MOD_VERT,
	CMD_SET_PULSE,
};

enum AXIS {
	AXIS_HORZ = 0,
	AXIS_VERT,
	NUM_AXIS
};

int vert_dir;
int horz_dir;

int w_horz;
int w_vert;

int horz_delay;
int vert_delay;
int horz_T;
int vert_T;
bool horz_up;
bool vert_up;

int prev_horz_dir;
int prev_vert_dir;

int speed_mod_horz;
int speed_mod_vert;

int pulse;

int next_axis;

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

	next_axis = AXIS_HORZ;

	speed_mod_horz = 28000;
	speed_mod_vert = 28000;

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
				horz_T = speed_mod_horz/w_horz;
				if (prev_horz_dir != horz_dir) {
					digitalWrite(HORZ_DIR_PIN, horz_dir);
					delayMicroseconds(1);
					prev_horz_dir = horz_dir;
			 }
				digitalWrite(HORZ_OUT_PIN, 1);
				horz_delay = pulse;
				horz_up = true;
			} else {
				horz_delay = 150;
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
				vert_T = speed_mod_vert/w_vert;
				if (prev_vert_dir != vert_dir) {
					digitalWrite(VERT_DIR_PIN, vert_dir);
					delayMicroseconds(1);
					prev_vert_dir = vert_dir;
				}
				digitalWrite(VERT_OUT_PIN, 1);
				vert_delay = pulse;
				vert_up = true;
			} else {
				vert_delay = 150;
			}
		}
	}

	min_delay = min(vert_delay, horz_delay);

	delayMicroseconds(min_delay);
	horz_delay -= min_delay;
	vert_delay -= min_delay;

	yield();
}

void speed_test_horz()
{
	int T = speed_mod_horz / 100;
	unsigned long start_time, end_time, total_time;

	start_time = millis();

	digitalWrite(HORZ_DIR_PIN, 1);
	delayMicroseconds(1);

	for (int i = 0; i < 180*40; i++) {
		digitalWrite(HORZ_OUT_PIN, 1);
		delayMicroseconds(pulse);
		digitalWrite(HORZ_OUT_PIN, 0);
		delayMicroseconds(T - pulse);
	}

	digitalWrite(HORZ_DIR_PIN, 0);
	delayMicroseconds(1);

	for (int i = 0; i < 180*40; i++) {
		digitalWrite(HORZ_OUT_PIN, 1);
		delayMicroseconds(pulse);
		digitalWrite(HORZ_OUT_PIN, 0);
		delayMicroseconds(T - pulse);
	}

	end_time = millis();

	total_time = end_time - start_time;

	//unsigned long is 4 bytes long, serial sends LSB byte first
	Serial.write((char *)total_time, 4);
}

void speed_test_vert()
{
	int T = speed_mod_vert / 100;
	unsigned long start_time, end_time, total_time;

	start_time = millis();

	digitalWrite(VERT_DIR_PIN, 1);
	delayMicroseconds(1);

	for (int i = 0; i < 180*10; i++) {
		digitalWrite(VERT_OUT_PIN, 1);
		delayMicroseconds(pulse);
		digitalWrite(VERT_OUT_PIN, 0);
		delayMicroseconds(T - pulse);
	}

	digitalWrite(VERT_DIR_PIN, 0);
	delayMicroseconds(1);

	for (int i = 0; i < 180*10; i++) {
		digitalWrite(VERT_OUT_PIN, 1);
		delayMicroseconds(pulse);
		digitalWrite(VERT_OUT_PIN, 0);
		delayMicroseconds(T - pulse);
	}

	end_time = millis();

	total_time = end_time - start_time;

	//unsigned long is 4 bytes long, serial sends LSB byte first
	Serial.write((char *)total_time, 4);
}

void set_speed_mod(enum AXIS axis, int val)
{
	if (axis == AXIS_HORZ)
		speed_mod_horz = val;
	else if (axis == AXIS_VERT)
		speed_mod_vert = val;
}

void set_pulse(int val)
{
	pulse = val;
}

void set_speed(int w, enum AXIS axis)
{
	int dir;
	if (w >= 0 && w <= 100)
			dir = 1;
	else {
			w = 256 - w;
			dir = 0;
	}

	if (axis == AXIS_HORZ) {
		w_horz = w;
		horz_dir = !dir;
	} else if (axis == AXIS_VERT) {
		w_vert = w;
		vert_dir = dir;
	}
}

void read_command()
{
	int cmd, val;
	cmd = Serial.read();

	if ((cmd >= 0 && cmd <= 100) || cmd >= 156) {
		set_speed(cmd, next_axis);
		next_axis = (next_axis + 1) % NUM_AXIS;
	} else {
		switch(cmd) {
			case CMD_RESET:
				set_speed(0, AXIS_HORZ);
				set_speed(0, AXIS_VERT);
				next_axis = AXIS_HORZ;
				speed_mod_horz = 28000;
				speed_mod_vert = 28000;
				pulse = 100;
				break;

			case CMD_SPEED_TEST_HORZ:
				speed_test_horz();
				break;

			case CMD_SPEED_TEST_VERT:
				speed_test_vert();
				break;

			case CMD_SET_SPEED_MOD_HORZ:
				while(!Serial.available())
					;
				val = 1000 * Serial.read();
				set_speed_mod(AXIS_HORZ, val);
				break;

			case CMD_SET_SPEED_MOD_VERT:
				while(!Serial.available())
					;
				val = 1000 * Serial.read();
				set_speed_mod(AXIS_VERT, val);
				break;

			case CMD_SET_PULSE:
				while(!Serial.available())
					;
				val = 10 * Serial.read();
				set_pulse( val);
				break;

			default:
				// Unknown command, do nothing
				break;
		}
	}
}

void loop()
{
	while(!Serial.available()) yield();
	read_command();

	yield();
}
