import os
import re
import http.server
import socketserver
import http.cookies
import urllib.parse
import urllib.request
import urllib.error

# Get settings from environment variables.
BIND_HOST = os.environ.get("BIND_HOST", "localhost")
BIND_PORT = int(os.environ.get("BIND_PORT", "8000"))
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001").rstrip('/')
LOGIN_PATH = os.environ.get("LOGIN_PATH", "/login")
LOGOUT_PATH = os.environ.get("LOGOUT_PATH", "/accounts/logout/")
SESSION_COOKIE_NAME = os.environ.get("SESSION_COOKIE_NAME", "iam_session")
IAM_USERNAME_HEADER = os.environ.get("IAM_USERNAME_HEADER", "IAM-Username")
IAM_EMAIL_HEADER = os.environ.get("IAM_EMAIL_HEADER", "IAM-Email")

class Handler(http.server.SimpleHTTPRequestHandler):
  def do_GET(self):
    return self.handle_request('GET')

  def do_POST(self):
    return self.handle_request('POST')

  def handle_request(self, method):
    # Handle an incoming request.

    # Logout.
    if (self.path+"?").startswith(LOGOUT_PATH+"?"):
      # Clear the session, which will result in the login page coming up.
      self.send_response(302)
      self.send_header("Location", LOGIN_PATH)
      self.send_header("Set-Cookie", SESSION_COOKIE_NAME + "=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT")
      self.end_headers()
      return

    # Check if a session is open.
    cookies = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
    if SESSION_COOKIE_NAME not in cookies:
      # The user doesn't have a session. Show a login page when requesting
      # the login path with GET. When requesting that path with POST,
      # start a new user session. Otherwise, redirect to the login path.
      if (self.path+"?").startswith(LOGIN_PATH+"?"):
        if method == "POST":
          # Start a session and redirect back to the origin path if a 'path'
          # parameter is in the query string. Get the username and email
          # from the form.
          #form = cgi.FieldStorage(fp=self.rfile, headers=self.headers)
          form = urllib.parse.parse_qs(self.rfile.read(int(self.headers['Content-Length'])))
          if b"username" in form and b"email" in form:
            self.send_response(302)
            self.send_header("Set-Cookie",
              SESSION_COOKIE_NAME + "=" + urllib.parse.urlencode(form, doseq=True))
            qs = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
            self.send_header("Location", qs['path'][0] if 'path' in qs else "/")
            self.end_headers()
            return

        self.send_response(403)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        with open("login_page.html", "rb") as login_page:
          self.copyfile(login_page, self.wfile)
        return
      else:
        # Redirect to the login page.
        self.send_response(302)
        self.send_header("Location",
          LOGIN_PATH + "?" + urllib.parse.urlencode({ "path": self.path }))
        self.end_headers()
        return

    # Extract session info from the session cookie.
    session_info = urllib.parse.parse_qs(cookies[SESSION_COOKIE_NAME].value)

    # Proxy the authenticated request.
    self.proxy_request(method, session_info)

  def proxy_request(self, method, session_info):
    # Read the request body if the method has one.
    try:
      body = self.rfile.read(int(self.headers['Content-Length']))
    except:
      body = None

    # Create the proxy request. Add identity headers last, so that
    # they clobber any client-set values for those headers. Pass
    # the Host: header unchanged. Add an X-Forwarded-For header.
    headers = dict(self.headers) # clone
    headers.update({
      IAM_USERNAME_HEADER: session_info["username"][0],
      IAM_EMAIL_HEADER: session_info["email"][0],
      "X-Forwarded-For": ((headers["X-Forwarded-For"] + ", ") if "X-Forwarded-For" in headers else "")
         + self.client_address[0]
    })

    # Set Host (see https://tools.ietf.org/html/rfc7230#section-5.4) for Django to read
    headers["Host"] = re.sub('^https?://', '', BACKEND_URL, flags=re.IGNORECASE)

    # Build request
    req = urllib.request.Request(
            BACKEND_URL + self.path,
            data=body,
            headers=headers,
            method=method)

    # Send the request and pipe the response back.
    try:
      resp = urllib.request.urlopen(req)
    except (ConnectionResetError, BrokenPipeError) as e:
        self.send_response(500)
        self.send_header("Content-Type", "text/plain; charset=utf8")
        self.end_headers()
        self.wfile.write(str(e).encode("utf8"))
    except urllib.error.HTTPError as err:
      # Non-200 OK responses come here, but we can use err as
      # the response, conveniently.
      resp = err

    # Copy the status code and headers.
    self.send_response(resp.getcode())
    for k, v in resp.info().items():
      self.send_header(k, v)
    self.end_headers()

    # Pipe the body.
    self.copyfile(resp, self.wfile)

# Configure the server and handler.
socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer((BIND_HOST, BIND_PORT), Handler)

# Begin listening for connections.
print("Authentication headers: " + IAM_USERNAME_HEADER + ", " + IAM_EMAIL_HEADER + ".")
print("Forwarding http://" + BIND_HOST + ":" + str(BIND_PORT) + " to " + BACKEND_URL + ".")
httpd.serve_forever()
