# Copyright 2017 Google Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
 
 
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
PORT = int(os.environ.get("PORT", "8080"))
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(bytes("""
        <!doctype html><html>
    <head><title>ESP Sample App</title><link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"></head>
    <body>
    <div class="container">
    <div class="row">
    <div class="col s2">&nbsp;</div>
    <div class="col s8">
    <div class="card blue">
        <div class="card-content white-text">
            <h4>Hello %s</h4>
        </div>
        <div class="card-action">
            <a href="/_gcp_iap/identity">Identity JSON</a>
            <a href="/_gcp_iap/clear_login_cookie">Logout</a>
        </div>
    </div></div></div></div>
    </body></html>
        """ % self.headers.get("x-goog-authenticated-user-email","unauthenticated user").split(':')[-1], "utf8"))
print("Listing on port", PORT)
server = HTTPServer(('0.0.0.0', PORT), RequestHandler)
server.serve_forever()
