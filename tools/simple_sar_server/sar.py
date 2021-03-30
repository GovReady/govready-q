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

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import uuid


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

        if self.path == "/":
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
                    "name": random.choice([f"Weekly Scan {random.randint(1, 50)}",
                                           f"Daily Scan {random.randint(1, 365)}",
                                           f"Build Scan {random.randint(25, 100)}"
                                         ]),
                    "system_id": 132,
                    "sar": sar_list,
                    "assessment-results": {},
                    "uuid": "14d593bf-38e9-4702-9367-9e11081f79e1",
                    "metadata": {
                        "title": random.choice([f"Weekly Scan {random.randint(1, 50)}",
                                                f"Daily Scan {random.randint(1, 365)}",
                                                f"Build Scan {random.randint(25, 100)}"
                                               ]),
                        "published": "dateTime-with-timezone",
                        "last-modified": "dateTime-with-timezone",
                        "schema": "GovReadySimpleSAR",
                        "system_id": 132,
                        "version": "0.2"
                    }
            }

            # Send the JSON response
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        elif self.path == "/hello":
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

httpd = HTTPServer(('localhost', 8888), SimpleHTTPRequestHandler)
httpd.serve_forever()