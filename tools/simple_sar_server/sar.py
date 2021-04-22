#!/usr/bin/env python3

########################################################
#
# A simple Python webserver to generate random
# assessment results
#
# Usage:
#   python sar.py
#
# Accessing:
#   curl localhost:8888
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


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def mk_sar(self):

        sar = {
            "id": f"{random.randint(20431, 34554)}",
            "name": "oscap-scan",
            "description": "SCAP scan Results",
            "ip": f"10.10.0.{str(random.randint(2, 250))}",
            "uuid": f"{str(uuid.uuid4())}",
            "pass": random.randint(200, 300),
            "fail": random.randint(0, 20),
            "error": random.randint(0, 4)
        }

        return sar

    def do_GET(self, method=None):

        # Parse path
        # print("urlparse(self.path)", urlparse(self.path))
        parsed_path = urlparse(self.path)
        # print("parsed_path", parsed_path)
        # Parse query params
        # print("parsed_path.query",parsed_path.query)
        params = parse_qs(parsed_path.query)
        print("** params", params)
        # params are received as arrays, so get first element in array
        system_id = params.get('system_id', [0])[0]
        deployment_uuid = params.get('deployment_uuid', ['None'])[0]
        if deployment_uuid == 'None':
            deployment_uuid = None

        # Route and handle request
        if parsed_path.path == "/":
            """Reply with sample sar"""
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Generate a random small number of endpoint assessments
            sar_list = []
            for endpoints in range(0,random.randint(1, 4)):
                sar_list.append(self.mk_sar())
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

        elif parsed_path.path == "/hello":
            """Reply with "hello"""""
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            data = {"message":"hello"}
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
    httpd = HTTPServer(('localhost', 8888), SimpleHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    main()
