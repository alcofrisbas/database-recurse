import socket

# pretty colors
red = "\033[1;31m"
green = "\033[1;32m"
yellow = "\033[1;33m"
blue = "\033[1;34m"
defcol = "\033[0m"

"""
A basic packet class for easy string sending.
"""
class Packet:
    def __init__(self, response_body=[]):
        # set up headers
        self.response_headers = {
            'Content-Type': 'text/html; encoding=utf8',
            'Content-Length': 0,
            'Connection': 'close',
        }
        self.response_body = response_body
        self.response_proto = 'HTTP/1.1'
        self.response_status = '200'
        self.response_status_text = 'OK'

    # encode for sending and concat all data
    def encode(self,encoding="utf-8"):
        response_body_raw = ''.join(self.response_body)
        self.response_headers['Content-Length'] = len(response_body_raw)
        response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                               self.response_headers.items())
        proto = self.response_proto + " " + self.response_status + ' ' + self.response_status_text + "\n"

        s = proto + response_headers_raw + "\n" + response_body_raw
        return s.encode(encoding)



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# so you can reboot quicker
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
port = 4000
s.bind(('', port))
print("Binding to port {}{}{}".format(green,str(port), defcol))
s.listen(5)
print("Listening...")

# little in-memory key value database
inMemory = {}

# when path == set
def set_key(c, req):
    query = req[1]
    response_body = []

    # set value
    for item in query.split("&"):
        key = item.split("=")[0]
        value = item.split("=")[1]
        inMemory[key] = value
        print("setting key {}{}{} to value {}{}{}".format(green, key, defcol, green, value, defcol))
        response_body.append('{{"{}":"{}"}}'.format(key, value))

    p = Packet(response_body=response_body)
    c.sendall(p.encode())

# when path == get
def get_key(c, req):
    # parse query
    query = req[1]
    response_body = []
    items = query.split("&")

    # retrieve value
    if len(items) == 1:
        key = items[0].split("=")[0]
        value = items[0].split("=")[1]
        if key == "key":
            if inMemory.get(value, None):
                print("getting key {}{}{} value is {}{}{}".format(green, value, defcol, green, inMemory[value], defcol))
            else:
                print("key {}{}{} is {}null{}".format(green, value, defcol, red, defcol))
            response_body.append('{{"{}":"{}"}}'.format(value, inMemory.get(value, "null")))
        else:
            response_body.append('{{"error_msg":"invalid arg:{}"}}'.format(key))

    p = Packet(response_body=response_body)
    c.sendall(p.encode())


while True:
    try:
        c, addr = s.accept()
        print("accepting incoming connection: {}{}{} port {}{}{}".format(green, addr[0], defcol, green, addr[1], defcol),end="\t")

        # quick parse of request for path and query
        msg = c.recvmsg(4096)
        msg = msg[0].decode("utf-8").split(" ")[1][1:]
        req = msg.split("?")
        path = req[0]

        # route by path and query
        if path == "set":
            set_key(c, req)
        elif path == "get":
            get_key(c, req)
        # catchall
        else:
            p = Packet(response_body=['{"error_msg":"invalid path"}'])
            c.sendall(p.encode())

        c.close()
    except KeyboardInterrupt:
        break

print("\nClosing")