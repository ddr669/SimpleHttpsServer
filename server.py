
import http.server
#import ssl
import os.path
import sys
import urllib
import html
import io

from sys import argv


DEV_SIG = "__DDr669__"

def get_passwd_in_env(filename: str = '.env') -> str:
    password = None
    if os.path.exists('.env'):
        tls_op = 'tls_password='
        with open('.env', 'r') as file:
            for line in file:
                if line[:len(tls_op)] == tls_op:
                    password = line[len(tls_op):].strip()                
    return password


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str = None, **kwargs):
        for c, p in enumerate(argv):
            if p[:2] == '-d':
                try:
                    self.directory = argv[c+1]
                except IndexError:
                    print('[!] Missing Arguments ')
                    self.directory = None
        
        super().__init__(*args,directory=self.directory,**kwargs)


    def do_GET(self):
        if self.path == "/home/":
            self.path = 'index.html'

        super().do_GET() 


    def do_POST(self):
        super().do_POST()

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(
                http.server.HTTPStatus.NOT_FOUND,
                "No permission to list directory")
            return None

        list.sort(key=lambda a: a.lower())
        r = []
        displaypath = self.path
        displaypath = displaypath.split('#', 1)[0]
        displaypath = displaypath.split('?', 1)[0]
        try:
            displaypath = urllib.parse.unquote(displaypath,
                                errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(displaypath)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        title = f'Directory listing for {displaypath}'
        r.append('<!DOCTYPE HTML>')
        r.append('<html lang="en">')
        r.append('<head>')
        r.append(f'<meta charset="{enc}">')
        r.append('<style type="text/css">\n:root {\ncolor-scheme: light dark;\n}\n</style>')
        r.append(f'<title>{title}</title>\n</head>')
        r.append(f'<body>\n<h1>{title}</h1>')
        r.append('<hr>\n<ul>')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            r.append('<li><a href="%s">%s</a></li>'
                    % (urllib.parse.quote(linkname,
                                          errors='surrogatepass'),
                       html.escape(displayname, quote=False)))
        r.append('</ul>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')

        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(http.server.HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Signature-Dev", f"Ass: -{DEV_SIG}-")
        self.end_headers()
        return f

host     = '192.168.1.104'
port     = 443
password = get_passwd_in_env()

# print(password)
httpd = http.server.HTTPServer((host,port), 
            Handler,
            True,
            keyfile='key.pem',
            certfile='cert.pem',
            password=password)


#context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
#httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
httpd.serve_forever()

