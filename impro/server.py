from http.server import HTTPServer, BaseHTTPRequestHandler, HTTPStatus
import urllib.parse

from .site import Site

global_site = None
global_files = []


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)

        for filename, content in global_files:
            filename = str(filename)
            if filename != path:
                continue

            if filename.endswith(".html"):
                content_type = "text/html"
            elif filename.endswith(".css"):
                content_type = "text/css"
            else:
                content_type = ""

            if isinstance(content, str):
                content = content.encode("utf-8")

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", content_type)
            self.send_header("Content-Length", str(len(content)))
            #self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_file_listing()
        #return self.send_error(HTTPStatus.NOT_FOUND)

    def send_file_listing(self):
        markup = '<ul>'
        for filename, content in global_files:
            markup += f'<li><a href="{filename}">{filename}</a> {len(content):,d}</li>'
        markup += '</ul>'

        markup = markup.encode("utf-8")

        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(markup)))
        self.end_headers()
        self.wfile.write(markup)


def run_server(site: Site):
    global global_site, global_files
    global_site = site
    global_files = list(site.iter_files("html"))
    server = HTTPServer(("", 8000), RequestHandler)
    server.serve_forever()

