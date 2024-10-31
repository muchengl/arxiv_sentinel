from http.server import BaseHTTPRequestHandler

from utils.utils import run


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write('arXiv email job trigger......'.encode('utf-8'))

        run()

        return
