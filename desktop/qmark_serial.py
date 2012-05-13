import os
import time

from arduino_serial import SerialPort

COMMAND_LIGHT_OFF = 'D'
COMMAND_LIGHT_ON = 'L'
COMMAND_SOUND_COIN = 'C'
COMMAND_SOUND_ONE_UP = 'O'
COMMAND_PAUSE = 'P'


def guess_port_filename():
    dev_dir = '/dev'
    prefix = 'tty.usb'
    for filename in os.listdir(dev_dir):
        if filename.startswith(prefix):
            return os.path.join(dev_dir, filename)


class QuestionMarkLamp(object):
    def __init__(self, port_name):
        super(QuestionMarkLamp, self).__init__()

        self.serial_port = SerialPort(port_name, 9600)

        # Arduino resets when the serial port is open, give it time to boot up.
        time.sleep(5)

    def light_off(self):
        self._write(COMMAND_LIGHT_OFF)

    def light_on(self):
        self._write(COMMAND_LIGHT_ON)

    def play_coin_sound(self):
        self._write(COMMAND_SOUND_COIN)

    def play_one_up_sound(self):
        self._write(COMMAND_SOUND_ONE_UP)

    def pause(self, n=1):
        self._write(COMMAND_PAUSE * n)

    def _write(self, s):
        self.serial_port.write(s)


def main():
    port_filename = guess_port_filename()
    question_mark_lamp = QuestionMarkLamp(port_filename)
    for i in range(5):
        question_mark_lamp.light_on()
        question_mark_lamp.pause(5)
        question_mark_lamp.light_off()
        question_mark_lamp.pause(5)

    # Give the commands time to execute before the port is closed.
    time.sleep(3)

if __name__ == '__main__':
    main()
