
from http.server import HTTPServer, BaseHTTPRequestHandler
import json 


socket = None
class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            image_id = self.path.split('/')[1]
            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()

            result = {'image_id': image_id}

            result = json.dumps(result)
            self.wfile.write(result.encode()) 
        except BaseException as ex:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'ERROR:') 
            print(ex)
        return


server_address = ('0.0.0.0', 8000)
with HTTPServer(server_address, myHandler) as httpd:
    socket = httpd
    httpd.handle_request()
