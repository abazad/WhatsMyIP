#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a simple "What's My IP" Server:
It returns the REMOTE_ADDR to connecting clients.

It is written in Python and requires Python 3.3+

Written in 2013/2014 by Philipp Klaus <philipp.l.klaus →AT→ web.de>.
Check <https://github.com/pklaus/WhatsMyIP> for newer versions.
"""

import time
import socket
import http.server
import ipaddress
import urllib.parse

CONSIDER_XREALIP = False

class RequestHandler(http.server.BaseHTTPRequestHandler):
    """
    A request handler that can only return the
    REMOTE_ADDR - the IP of the connecting node.
    """
    def do_HEAD(s):
        """ Respond to a HEAD request. """
        s.send_response(200)
        s.send_header("Content-type", "text/plain")
        s.end_headers()
    def do_GET(s):
        """ Respond to a GET request. """
        parsed_path = urllib.parse.urlparse(s.path)
        path = parsed_path[2]
        if path == '/':
            RequestHandler.do_HEAD(s)
            address = None
            if CONSIDER_XREALIP:
                address = s.headers.get('X-Real-IP')
            if not address: address = s.client_address[0]
            ip = ipaddress.ip_address(address)
            if ip.version == 6 and ip.ipv4_mapped: ip = ip.ipv4_mapped
            s.wfile.write(str(ip).encode('ascii'))
        elif path == '/favicon.ico':
            s.send_response(200)
            s.send_header('Content-type', 'image/png')
            s.end_headers()
            with open('favicon.png', 'rb') as f:
                s.wfile.write(f.read())
        else:
            s.send_response(404)
            s.send_header("Content-type", "text/plain")
            s.end_headers()
            s.wfile.write("404 - Not found".encode('ascii'))
    def address_string(s):
        address = None
        if CONSIDER_XREALIP:
            address = s.headers.get('X-Real-IP')
        if not address: address = s.client_address[0]
        ip = ipaddress.ip_address(address)
        if ip.version == 6 and ip.ipv4_mapped:
            return "::ffff:" + str(ip.ipv4_mapped)
        else:
            return str(ip)
    def version_string(self):
        return 'WhatsMyIP/Python'
    def log_request(self, code='-', size='-'):
        """ Log accepted requests. """
        fmt = '"{request}" {code} {size} "{referer}" "{useragent}"'
        message = fmt.format(request=self.requestline, code=code, size=size,
                             referer=self.headers.get('referer', ''),
                             useragent=self.headers.get('user-agent', ''))
        self.log_message(message)
    def log_date_time_string(self):
        """Return the current time formatted for logging."""
        now = time.time()
        year, month, day, hh, mm, ss, x, y, z = time.gmtime(now)
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (
                day, self.monthname[month], year, hh, mm, ss)
        return s

class HTTPServerV6(http.server.HTTPServer):
    """ IPv6 enabled version of HTTPServer """
    address_family = socket.AF_INET6

def main():
    global CONSIDER_XREALIP

    import argparse
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--host', default='::', help='IPv6 to bind to. Default is "::".')
    parser.add_argument('--port', default=8080, type=int, help='Port to listen at. Default is 8080.')
    parser.add_argument('--consider-xrealip', action="store_true", help='If you want the header X-Real-IP to be considered, set this arg.')

    args = parser.parse_args()

    if args.consider_xrealip: CONSIDER_XREALIP = True

    httpd = HTTPServerV6((args.host, args.port), RequestHandler)
    print(time.asctime(), "Server Starts - %s:%s" % (args.host, args.port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (args.host, args.port))

if __name__ == '__main__':
    main()

