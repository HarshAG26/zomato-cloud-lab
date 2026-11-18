"""Educational, dependency-free food delivery demo. No payments or user data."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json, os, time, socket, threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REGION = os.getenv('AWS_REGION', 'local')
RESTAURANTS = [
    {'id': 1, 'name': 'Spice Bowl', 'dish': 'Paneer Rice Bowl', 'price': 179},
    {'id': 2, 'name': 'Pizza Corner', 'dish': 'Margherita Pizza', 'price': 229},
    {'id': 3, 'name': 'Dosa House', 'dish': 'Masala Dosa', 'price': 129},
]
ORDERS = []  # Per-instance only: not shared or durable across replicas.
LOCK = threading.Lock()
class Handler(BaseHTTPRequestHandler):
    def respond(self, code, body, content_type='application/json'):
        payload = json.dumps(body).encode() if not isinstance(body, bytes) else body
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)
    def do_GET(self):
        route = urlparse(self.path).path
        if route == '/':
            return self.respond(200, (ROOT / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        if route == '/health':
            return self.respond(200, {'status':'ok'})
        if route == '/api/restaurants':
            return self.respond(200, {'restaurants': RESTAURANTS})
        if route == '/api/info':
            return self.respond(200, {'region': REGION, 'instance': socket.gethostname(), 'storage':'in-memory demo'})
        if route == '/api/cpu':
            # Deliberately bounded work for controlled scaling experiments.
            end = time.monotonic() + 0.12
            x = 1
            while time.monotonic() < end:
                x = (x * 1664525 + 1013904223) % 4294967296
            return self.respond(200, {'status':'completed', 'value':x})
        return self.respond(404, {'error':'not found'})
    def do_POST(self):
        if urlparse(self.path).path != '/api/orders':
            return self.respond(404, {'error':'not found'})
        try:
            length = int(self.headers.get('Content-Length','0'))
            if length < 1 or length > 1024:
                return self.respond(400, {'error':'invalid request size'})
            data = json.loads(self.rfile.read(length))
            item_id = data.get('restaurant_id')
            if type(item_id) is not int or item_id not in [r['id'] for r in RESTAURANTS]:
                return self.respond(400, {'error':'invalid restaurant_id'})
            with LOCK:
                order_id = len(ORDERS) + 1
                ORDERS.append({'id':order_id, 'restaurant_id':item_id})
            return self.respond(201, {'order_id':order_id, 'message':'Demo order placed (not persistent)'})
        except (ValueError, TypeError, json.JSONDecodeError):
            return self.respond(400, {'error':'invalid JSON'})
    def log_message(self, fmt, *args):
        print('%s %s' % (self.address_string(), fmt % args), flush=True)
if __name__ == '__main__':
    port = int(os.getenv('PORT','8080'))
    print(f'Listening on {port}; region={REGION}', flush=True)
    ThreadingHTTPServer(('0.0.0.0',port), Handler).serve_forever()
