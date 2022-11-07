#!/usr/bin/env python3

##############################################################
#
# A simple Python webserver to generate mock CSAM API results
#
# Usage:
#   
#   # Start mock service
#   python3 integrations/csam/mock.py
#
# Accessing:
#
#   curl localhost:9002/endpoint
#   curl -X 'GET' 'http://127.0.0.1:9002/v1/system/111'
#   curl localhost:9002/v1/system/111  # requires authentication
#
# Accessing with simple authentication:
#
#   curl -X 'GET' \
#   -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' \
#   -H 'Authorization: Bearer FAD619' \
#   'http://localhost:9002/v1/systems/111'
#
#    curl -X 'GET' -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' -H 'Authorization: Bearer FAD619' 'http://localhost:9002/v1/systems/111'
#
##############################################################

from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from abc import ABC
#from urllib.parse import urlparse
from django.utils import timezone
from time import time


HOSTNAME = 'localhost'
PORT = 9002
MOCK_SRVC = "CSAM"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def mk_csam_system_info_response(self, system_id):
        """Return system information from working mock data"""
        with open(self.systems_file, 'r') as f:
            systems = json.load(f)
        return systems[system_id] if system_id in systems else self.return_404(f'No system with id {system_id} exists.')

    def update_systems(self, system_id, updates):
        """Update system information in working mock data"""
        with open(self.systems_file, 'r') as f:
            systems = json.load(f)
        if system_id in systems:
            system = systems.get(system_id)
            for key in updates.keys():
                print(f'Updating system {system_id} key "{key}" with "{updates[key]}"')
                system[key] = updates[key]
            with open(self.systems_file, 'w') as f:
                json.dump(systems, f, indent = 4)
        else:
            self.return_404(f'No system with id {system_id} exists.')

    def return_404(self, message):
        """Return a 404 message"""
        print(message)
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        data = {"message": message}
        self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

    def do_GET(self, method=None):
        """Parse and route GET request"""
        # Parse path
        request = urlparse(self.path)
        params = parse_qs(request.query)
        print(f"request.path: {request.path}, params: {params}")
        # params are received as arrays, so get first element in array
        # system_id = params.get('system_id', [0])[0]

        # Route GET request
        if request.path == "/v1/test/hello":
            """Reply with 'hello'"""
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = {"message":"hello"}
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        elif request.path == "/v1/test/authenticate-test":
            """Test authentication"""
            if 'Authorization' in self.headers:
                print("Authorization header:", self.headers['Authorization'])
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                data = {"reply": "Success",
                        "Authorization": self.headers['Authorization'],
                        "pat": self.headers['Authorization'].split("Bearer ")[-1]
                        }
            else:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                data = {"reply": "Fail",
                        "Authorization": None,
                        "pat": None
                        }
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        elif request.path == "/v1/systems/111" or request.path == "/v1/systems/222":
            """Reply with system information"""

            # system_id = re.search(r"/v1/systems/([0-9]{1,8})", request.path).group(1).strip()
            pat = None
            if 'Authorization' in self.headers:
                pat = self.headers['Authorization'].split("Bearer ")[-1]
            if pat is None or pat != "FAD619":
                # Authentication fails
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                data = {"reply": "Fail",
                        "Authorization": None,
                        "pat": None
                        }
            else:
                # Authentication succeeds
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                if '111' in request.path:
                    data = self.mk_csam_system_info_response('111')
                elif '222' in request.path:
                    data = self.mk_csam_system_info_response('222')
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        else:
            """Reply with Path not found"""
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = {"message":"Path not found"}
            # Send the JSON response
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

    def do_POST(self):
        """Parse and route POST request"""
        request = urlparse(self.path)
        params = parse_qs(request.query)
        print("request.path:", request.path)
        print("** params", params)

        # Route POST request
        if request.path == "/v1/test/hello":
            """Reply with 'hello'"""
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = {"message": "hello, POST"}
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        if request.path == "/v1/systems/111" or request.path == "/v1/systems/222":
            pat = None
            if 'Authorization' in self.headers:
                pat = self.headers['Authorization'].split("Bearer ")[-1]
            if pat is None or pat != "FAD619":
                # Authorization failed
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                data = {"message": "Unauthorized request",
                        "endpoint": request.path
                        }
            else:
                # Authorization succeeded; read POST data and update system info
                content_length = int(self.headers['Content-Length'])
                self.post_data = self.rfile.read(content_length)
                self.post_data_json = json.loads(self.post_data)
                if '111' in request.path:
                    system_id = '111'
                elif '222' in request.path:
                    system_id = '222'
                print(100, self.post_data_json)
                self.update_systems(system_id, self.post_data_json)
                # Send the JSON response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                data = self.mk_csam_system_info_response(system_id)
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        else:
            # Path not found
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = {"message":"Path not found"}
            # Send the JSON response
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

def main():

    print('Loading initial system data')
    mock_data_dir = Path.joinpath(Path(__file__).resolve().parent, 'assets', 'data')
    mock_data_file = Path.joinpath(mock_data_dir, 'systems.json')
    with open(Path.joinpath(mock_data_dir, 'src_systems.json'), 'r') as f:
        systems = json.load(f)
    print('Creating system data working file')
    with open(mock_data_file, 'w') as f:
        json.dump(systems, f, indent = 4)
    print('Starting simple web server')
    SimpleHTTPRequestHandler.systems_file = mock_data_file
    print(f'Providing mock data on {len(systems)} systems with IDs: 111, 222')
    httpd = HTTPServer((HOSTNAME, PORT), SimpleHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
