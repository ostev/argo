from http.server import BaseHTTPRequestHandler


def respond(handler: BaseHTTPRequestHandler, text: str, content_type: str):
    handler.send_response(200)
    handler.send_header("Content-type", content_type)
    handler.end_headers()
    handler.wfile.write(bytes(text, "utf-8"))


def respond_html(handler: BaseHTTPRequestHandler, text: str):
    respond(handler, text, "text/html")


def respond_json(handler: BaseHTTPRequestHandler, text: str):
    respond(handler, text, "application/json")


def not_found(handler: BaseHTTPRequestHandler):
    handler.send_error(404)