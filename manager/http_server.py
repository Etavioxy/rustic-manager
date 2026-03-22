from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from typing import Callable, Optional
import time


class HeartbeatHandler(BaseHTTPRequestHandler):
    controller = None
    original_params = None
    last_heartbeat = 0
    timeout_seconds = 180
    
    def do_POST(self):
        if self.path == '/heartbeat':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body)
                self.handle_heartbeat(data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_heartbeat(self, data: dict):
        HeartbeatHandler.last_heartbeat = time.time()
        
        if HeartbeatHandler.controller:
            if HeartbeatHandler.original_params is None:
                HeartbeatHandler.original_params = {
                    'min': HeartbeatHandler.controller.min_interval,
                    'max': HeartbeatHandler.controller.max_interval,
                    'init': HeartbeatHandler.controller.init_interval
                }
            
            min_val = data.get('min', 1.5)
            max_val = data.get('max', 5)
            init_val = data.get('init', 3)
            
            HeartbeatHandler.controller.set_params(min_val, max_val, init_val)
            print(f"Heartbeat received, interval set to {min_val}/{max_val}/{init_val}")
    
    def log_message(self, format, *args):
        pass


def check_heartbeat_timeout():
    if HeartbeatHandler.original_params and HeartbeatHandler.controller:
        if time.time() - HeartbeatHandler.last_heartbeat > HeartbeatHandler.timeout_seconds:
            params = HeartbeatHandler.original_params
            HeartbeatHandler.controller.set_params(
                params['min'],
                params['max'],
                params['init']
            )
            print(f"Heartbeat timeout, restored to {params['min']}/{params['max']}/{params['init']}")
            HeartbeatHandler.original_params = None


class HTTPServerThread:
    def __init__(self, port: int = 8765):
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self, controller):
        HeartbeatHandler.controller = controller
        HeartbeatHandler.last_heartbeat = time.time()
        
        self.server = HTTPServer(('localhost', self.port), HeartbeatHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"HTTP server started on port {self.port}")
    
    def stop(self):
        if self.server:
            self.server.shutdown()
