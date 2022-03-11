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

    def mk_csam_system_info_response(self):
        csam_system_info_response = {
            "system_id": 111,
            "name": "My IT System"
        }
        return csam_system_info_response

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
            # header_type = type(self.headers)
            # header_dict = dict(self.headers)
            # print("headers ======\n", self.headers)
            # print("header_type ======\n", header_type)
            # print("header_dict ======\n", header_dict)
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
            #
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
