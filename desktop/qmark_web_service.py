import tornado.autoreload
import tornado.ioloop
import tornado.web

import qmark_serial

_request_handlers = []


class QuestionMarkHandler(tornado.web.RequestHandler):
    class __metaclass__(type(tornado.web.RequestHandler)):
        def __init__(cls, name, bases, class_dict):
            super(type(cls), cls).__init__(name, bases, class_dict)
            _request_handlers.append(cls)

    lamp = None

    name = None
    url = r'/'

    def get(self):
        self.send_command()
        for handler_class in _request_handlers:
            if handler_class.name is not None:
                self.write_link(handler_class.url, handler_class.name)

    def write_link(self, url, name):
        self.write('<a href="%s">%s</a><br>' % (url, name))

    def send_command(self):
        pass


class LightOffHandler(QuestionMarkHandler):
    name = 'Light Off'
    url = r'/light_off'

    def send_command(self):
        self.lamp.light_off()


class LightOnHandler(QuestionMarkHandler):
    name = 'Light On'
    url = r'/light_on'

    def send_command(self):
        self.lamp.light_on()


class PlayCoinSoundHandler(QuestionMarkHandler):
    name = 'Play Coin Sound'
    url = r'/play_coin_sound'

    def send_command(self):
        self.lamp.play_coin_sound()


class PlayOneUpSoundHandler(QuestionMarkHandler):
    name = 'Play One Up Sound'
    url = r'/play_one_up_sound'

    def send_command(self):
        self.lamp.play_one_up_sound()


class PauseHandler(QuestionMarkHandler):
    name = 'Pause'
    url = r'/pause'

    def send_command(self):
        self.lamp.pause()


def main():
    port_name = qmark_serial.guess_port_filename()
    QuestionMarkHandler.lamp = qmark_serial.QuestionMarkLamp(port_name)

    handlers = [tornado.web.url(h.url, h, name=h.name) for h in _request_handlers]
    application = tornado.web.Application(handlers)
    application.listen(8888)

    tornado.autoreload.start()
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
