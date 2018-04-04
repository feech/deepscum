from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from http.server import SimpleHTTPRequestHandler


class NN_Handler(BaseHTTPRequestHandler):
    # def __init__(self):
    #     self.commands=['GET']
    def do_GET(self):
        # print('get')
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(b'OK') #Doesnt work

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(b'OK') #Doesnt work
    	

# if __name__ == '__main__':

http = HTTPServer(('localhost', 5342), NN_Handler)
# http.serve_forever()
http.handle_request()


