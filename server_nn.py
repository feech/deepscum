from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from http.server import SimpleHTTPRequestHandler
import json

class NN_Handler(BaseHTTPRequestHandler):
    # def __init__(self):
    #     self.commands=['GET']
    def do_GET(self):
        # take image from redis
        # split, predict
        # send json-back
        print(self.path)
        im_id = self.path.split('/')[-1]
        imgt = load_img(im_id)
        X = split_img_to_100x100(imgt)
        yPred = cnn_rd.predict(X)
        vp = select_valid_predictions(yPred)

        input = [{'l':i[0], 't':i[1], 'w':o[3][0], 'h':o[3][1], 'x':o[2][0], 'y':o[2][1], 'component':o[0]} for i,o in [(area(o), o) for o in vp]]
        result = {'date': 'xz',
            'id': im_id,
            'survey': "",
            'input': input}


        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8')) 



if __name__ == '__main__':
    http = HTTPServer(('localhost', 5343), NN_Handler)
    # http.serve_forever()

http = HTTPServer(('localhost', 5342), NN_Handler)
for i in range(2):
    print('iteration %d'%i)
    http.handle_request()


