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

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        # Generate a random small number of endpoint assessments
        sar_list = []
        for endpoints in range(0,random.randint(1, 4)):
            sar_list.append(self.mk_sar())
        data = {"schema": "GovReadySimpleSAR",
                "version": "0.1",
                "sar": sar_list
        }

        # Send the JSON response
        self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))


httpd = HTTPServer(('localhost', 8888), SimpleHTTPRequestHandler)
httpd.serve_forever()