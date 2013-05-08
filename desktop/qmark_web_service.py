import Queue
import threading
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

import qmark_serial

PORT = 8888

commands = None
command_queue = Queue.Queue(100000)


class HTTPRequestHandler(BaseHTTPRequestHandler):

    def head(self):
        command_sequence = self.parse_command_sequence()
        if command_sequence is None:
            self.send_response(404)
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
        self.end_headers()
        return command_sequence

    def do_HEAD(self):
        self.head()

    def do_GET(self):
        command_sequence = self.head()
        body = 'no_body' not in self.query_string_dict
        if command_sequence is not None:
            if body:
                self.wfile.write('<html><head><title>qmark web service</title></head>')
                self.wfile.write('<body><p>')
            for command in command_sequence:
                command_queue.put(command)
            if body:
                base_path = self.path.rstrip('/')
                for name in sorted(commands):
                    self.wfile.write('<a href="%s/%s">%s</a><br>' % (base_path, name, name))
                self.wfile.write('</p></body></html>')

    def parse_command_sequence(self):
        path = self.path.lstrip('/').rstrip()

        if '?' in path:
            path, qs = path.split('?', 1)
            self.query_string_dict = urlparse.parse_qs(qs)
        else:
            self.query_string_dict = {}

        path = path.split('/')
        if path == ['']:
            return []
        try:
            command_sequence = [commands[name] for name in path]
        except KeyError:
            return None
        return command_sequence


def init_lamp_and_commands():
    port_name = qmark_serial.guess_port_filename()
    lamp = qmark_serial.QuestionMarkLamp(port_name)

    global commands
    commands = dict(
        light_off=lamp.light_off,
        light_on=lamp.light_on,
        play_coin_sound=lamp.play_coin_sound,
        play_one_up_sound=lamp.play_one_up_sound,
        pause=lamp.pause
    )


def command_thread():
    do_init = True
    while True:
        try:
            if do_init:
                init_lamp_and_commands()
                do_init = False
            command = command_queue.get()
            command()
        except Exception:
            do_init = True


def main():
    thread = threading.Thread(target=command_thread)
    thread.setDaemon(True)
    thread.start()

    server_address = ('', PORT)
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    try:
        httpd.serve_forever()
    finally:
        httpd.server_close()


if __name__ == '__main__':
    main()
