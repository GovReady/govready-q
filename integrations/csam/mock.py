#!/usr/bin/env python3

########################################################
#
# A simple Python webserver to generate mock CSAM API
# results
#
# Usage:
#   
#   # Start mock service
#   python3 integrations/csam/mock.py
#
# Accessing:
#   curl localhost:9002/endpoint
#   curl localhost:9002/hello
#   curl localhost:9002/system/111  # requires authentication
#
# Accessing with simple authentication:
#   curl -X 'GET' 'http://localhost:9002/system/111' \
#     -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' \
#     -H 'Authorization: Bearer FAD619'
#
#######################################################

# Parse command-line arguments
import click

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

PORT = 9002

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    SYSTEM = {
        "system_id": 111,
        "name": "My IT System",
        "description":  "This is a simple test system"
    }

    def mk_csam_system_info_response(self):
        return self.SYSTEM

    def do_GET(self, method=None):

        # Parse path
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        print("parsed_path.path:", parsed_path.path)
        print("** params", params)
        # params are received as arrays, so get first element in array
        system_id = params.get('system_id', [0])[0]

        # Route and handle request
        if parsed_path.path == "/hello":
            """Reply with 'hello'"""

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = {"message":"hello"}

            # Send the JSON response
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        elif parsed_path.path == "/authenticate-test":
            """Test authentication"""

            # Test authentication by reading headers and looking for 'Authentication'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Read headers
            print("Authorization header:", self.headers['Authorization'])

            data = {
                "reply": "yes",
                "Authorization": self.headers['Authorization'],
                "pat": self.headers['Authorization'].split("Bearer ")[-1]
            }
            # Send the JSON response
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        elif parsed_path.path == "/system/111":
            """Reply with system information"""

            # Usage:
            #
            # # authorized example
            # curl -X 'GET' 'http://localhost:9002/system/111' \
            # -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' \
            # -H 'Authorization: Bearer FAD619'
            #
            # # unauthorized example:
            # curl -X 'GET' 'http://localhost:9002/system/111' \
            # -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' 
            #

            pat = None
            if 'Authorization' in self.headers:
                pat = self.headers['Authorization'].split("Bearer ")[-1]

            if pat is None or pat != "FAD619":
                # Reply with unauthorized
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                data = {
                    "message": "Unauthorized request",
                    "endpoint": parsed_path.path
                }
            else:
                # Request is authenticated
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                data = self.mk_csam_system_info_response()

            # Send the JSON response
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

        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        print("parsed_path.path:", parsed_path.path)
        print("** params", params)

        # Route and handle request
        if parsed_path.path == "/hello":
            """Reply with 'hello'"""

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = {"message": "hello, POST"}

            # Send the JSON response
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        if parsed_path.path == "/system/111":
            """Update system information"""

            # Usage:
            #
            # # authorized example
            # curl -X 'POST' 'http://localhost:9002/system/111' \
            # -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' \
            # -H 'Authorization: Bearer FAD619'
            #
            # # unauthorized example:
            # curl -X 'POST' 'http://localhost:9002/system/111' \
            # -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true'
            #

            pat = None
            if 'Authorization' in self.headers:
                pat = self.headers['Authorization'].split("Bearer ")[-1]

            if pat is None or pat != "FAD619":
                # Reply with unauthorized
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                data = {
                    "message": "Unauthorized request",
                    "endpoint": parsed_path.path
                }
            else:
                # Request is authenticated - read POST data and update system info
                content_length = int(self.headers['Content-Length'])
                self.post_data = self.rfile.read(content_length)
                self.post_data_json = json.loads(self.post_data)
                # post_data_decoded = post_data.decode('utf-8')
                self.SYSTEM['name'] = self.post_data_json.get('name', self.SYSTEM['name'])
                self.SYSTEM['description'] = self.post_data_json.get('description', self.SYSTEM['description'])

                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

                data = self.mk_csam_system_info_response()
            # Send the JSON response
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))


        else:
            """Reply with Path not found"""
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            data = {"message":"Path not found"}
            # Send the JSON response
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

def main():
    httpd = HTTPServer(('localhost', PORT), SimpleHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
