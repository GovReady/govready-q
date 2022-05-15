#!/usr/bin/env python3

#############################################################
#
# A simple Python webserver to generate mock GRC API results
# 
# Requirements:
# 
#   pip install click
#
# Usage:
#   
#   # Start mock service
#   python3 integrations/grc/mock.py
#
# Accessing:
#
#   curl localhost:9022/endpoint
#   curl -X 'GET' 'http://127.0.0.1:9022/v1/systems/111'
#   curl localhost:9022/v1/system/111  # requires authentication
#
# Accessing with simple authentication:
#
#   curl -X 'GET' \
#     -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' \
#     -H 'Authorization: Bearer FAD619' \
#     'http://localhost:9022/v1/systems/111'
#
#    curl -X 'GET' -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' -H 'Authorization: Bearer FAD619' 'http://localhost:9022/v1/systems/111'
#
##############################################################

# Parse command-line arguments
import click

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from abc import ABC
#from urllib.parse import urlparse
from django.utils import timezone
from time import time


PORT = 9022
MOCK_SRVC = "GRC"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    # Mock data
    SYSTEMS = { "111": {"id": 111,
                       "externalId": "string",
                       "name": "System A",
                       "description": "This is a simple test system",
                       "acronym": "string",
                       "organization": "string",
                       "subOrganization": "string",
                       "operationalStatus": "string",
                       "systemType": "string",
                       "financialSystem": "string",
                       "classification": "string",
                       "contractorSystem": True,
                       "fismaReportable": True,
                       "criticalInfrastructure": True,
                       "missionCritical": True,
                       "purpose": "string",
                       "ombExhibit": "string",
                       "uiiCode": "string",
                       "investmentName": "string",
                       "portfolio": "string",
                       "priorFyFunding": 0,
                       "currentFyFunding": 0,
                       "nextFyFunding": 0,
                       "categorization": "string",
                       "fundingImportStatus": "string"
                       },
                "222": {"id": 222,
                       "externalId": "string",
                       "name": "System B",
                       "description": "This is another simple test system",
                       "acronym": "string",
                       "organization": "string",
                       "subOrganization": "string",
                       "operationalStatus": "string",
                       "systemType": "string",
                       "financialSystem": "string",
                       "classification": "string",
                       "contractorSystem": True,
                       "fismaReportable": True,
                       "criticalInfrastructure": True,
                       "missionCritical": True,
                       "purpose": "string",
                       "ombExhibit": "string",
                       "uiiCode": "string",
                       "investmentName": "string",
                       "portfolio": "string",
                       "priorFyFunding": 0,
                       "currentFyFunding": 0,
                       "nextFyFunding": 0,
                       "categorization": "string",
                       "fundingImportStatus": "string"
                       }
                }

    def mk_csam_system_info_response(self, system_id):
        return self.SYSTEMS[system_id]

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
            # Test authentication by reading headers and looking for 'Authentication'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            # Read headers
            if 'Authorization' in self.headers:
                # print("Authorization header:", self.headers['Authorization'])
                data = {"reply": "Success",
                        "Authorization": self.headers['Authorization'],
                        "pat": self.headers['Authorization'].split("Bearer ")[-1]
                        }
            else:
                data = {"reply": "Fail",
                        "Authorization": None,
                        "pat": None
                        }
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        elif request.path == "/v1/systems/111" or request.path == "/v1/systems/222":
        # elif re.search(r"/v1/systems/([0-9]{1,8})", request.path):
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
                data = {"message": "Unauthorized request",
                        "endpoint": request.path
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
        # print("** params", params)

        # Route POST request
        if request.path == "/v1/test/hello":
            """Reply with 'hello'"""
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = {"message": "hello, POST"}
            self.wfile.write(json.dumps(data, indent=4).encode('UTF-8'))

        if request.path == "/v1/systems/111" or request.path == "/v1/systems/222":
            """Update system information"""
            # # authorized example
            # curl -X 'POST' 'http://localhost:9002/system/111' \
            # -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true' \
            # -H 'Authorization: Bearer FAD619'
            #
            # # unauthorized example:
            # curl -X 'POST' 'http://localhost:9002/system/111' \
            # -H 'accept: application/json;odata.metadata=minimal;odata.streaming=true'
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
                # Authorization succeeded - read POST data and update system info
                content_length = int(self.headers['Content-Length'])
                self.post_data = self.rfile.read(content_length)
                self.post_data_json = json.loads(self.post_data)
                if '111' in request.path:
                    system_id = '111'
                elif '222' in request.path:
                    system_id = '222'
                self.SYSTEMS[system_id]['name'] = self.post_data_json.get('name', self.SYSTEM['name'])
                self.SYSTEM[system_id]['description'] = self.post_data_json.get('description', self.SYSTEM['description'])
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                data = self.mk_grc_system_info_response(system_id)
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
    """Main loop"""

    print(f"\nStarting service '{MOCK_SRVC}' running on port {PORT}...")
    print(f"Information on {len(dhs_sorns)} systems available\n")
    httpd = HTTPServer(('localhost', PORT), SimpleHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
