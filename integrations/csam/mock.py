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
import random
import uuid
from pprint import pprint

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
        # print("urlparse(self.path)", urlparse(self.path))
        parsed_path = urlparse(self.path)
        # print("parsed_path", parsed_path)
        # Parse query params
        # print("parsed_path.query",parsed_path.query)
        params = parse_qs(parsed_path.query)
        print("parsed_path.path:", parsed_path.path)
        print("** params", params)
        # params are received as arrays, so get first element in array
        system_id = params.get('system_id', [0])[0]
        deployment_uuid = params.get('deployment_uuid', ['None'])[0]
        if deployment_uuid == 'None':
            deployment_uuid = None

        # Route and handle request
        if parsed_path.path == "/hello":
            """Reply with 'hello'"""

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = {"message":"hello"}

            # Send the JSON response
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        elif parsed_path.path == "/systems":
            """Reply with sample CSAM API response for system information"""

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Generate a random small number of endpoint assessments
            sar_list = []
            for endpoints in range(0,random.randint(1, 4)):
                sar_list.append(self.mk_csam_system_info_response())
            data = {"schema": "GovReadySimpleSAR",
                    "version": "0.2",
                    "sar": sar_list,
                    "assessment-results": {},
                    "uuid": f"{str(uuid.uuid4())}",
                    "metadata": {
                        "title": random.choice([f"Weekly Scan {random.randint(1, 50)}",
                                                f"Daily Scan {random.randint(1, 365)}",
                                                f"Build Scan {random.randint(25, 100)}"
                                               ]),
                        "description": None,
                        "published": "dateTime-with-timezone",
                        "last-modified": "dateTime-with-timezone",
                        "schema": "GovReadySimpleSAR",
                        "version": "0.2",
                        "system_id": system_id,
                        "deployment_uuid": deployment_uuid
                    }
            }

            # Temporarily set descriptio to title
            data["metadata"]["description"] = data["metadata"]["title"]
            pprint(data)

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

def main():
    httpd = HTTPServer(('localhost', PORT), SimpleHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
