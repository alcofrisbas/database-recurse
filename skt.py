import socket

red = "\033[1;31m"
green = "\033[1;32m"
yellow = "\033[1;33m"
blue = "\033[1;34m"
defcol = "\033[0m"

class Packet:
    def __init__(self, response_body=[]):
        self.response_headers = {
            'Content-Type': 'text/html; encoding=utf8',
            'Content-Length': 0,
            'Connection': 'close',
        }
        self.response_body = response_body
        self.response_proto = 'HTTP/1.1'
        self.response_status = '200'
        self.response_status_text = 'OK'

    def encode(self,encoding="utf-8"):
        response_body_raw = ''.join(self.response_body)
        self.response_headers['Content-Length'] = len(response_body_raw)
        response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                               self.response_headers.items())
        proto = self.response_proto + " " + self.response_status + ' ' + self.response_status_text

        s = proto + response_headers_raw + "\n" + response_body_raw
        return s.encode(encoding)



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

whitelist = ['127.0.0.1']

port = 4000
s.bind(('', port))
print("Binding to port {}{}{}".format(green,str(port), defcol))
s.listen(5)
print("Listening")
d = {}

while True:
    try:
        c, addr = s.accept()
        print("accepting incoming connection: {}{}{} port {}{}{}".format(green, addr[0], defcol, green, addr[1], defcol))
        msg = c.recvmsg(4096)

        msg = msg[0].decode("utf-8").split(" ")[1][1:]
        req = msg.split("?")
        path = req[0]


        if path == "set":

            query = req[1]

            response_body = []

            for item in query.split("&"):
                key = item.split("=")[0]
                value = item.split("=")[1]
                d[key] = value
                print("setting key {}{}{} to value {}{}{}".format(green, key, defcol, green, value, defcol))
                response_body.append('{{"{}":"{}"}}'.format(key, value))

            p = Packet(response_body=response_body)
            c.sendall(p.encode())

        elif path == "get":
            query = req[1]
            response_body = []
            items = query.split("&")
            if len(items) == 1:
                key = items[0].split("=")[0]
                value = items[0].split("=")[1]
                if key == "key":
                    if d.get(value, None):
                        print("getting key {}{}{} value is {}{}{}".format(green, value, defcol, green, d[value], defcol))
                    else:
                        print("key {}{}{} is {}null{}".format(green, value, defcol, red, defcol))
                    response_body.append('{{"{}":"{}"}}'.format(value, d.get(value, "null")))
                else:
                    response_body.append('{{"error_msg":"invalid arg:{}"}}'.format(key))
            p = Packet(response_body=response_body)
            c.sendall(p.encode())

        else:
            response_body = ['{"error_msg":"invalid path"}']
            p = Packet(response_body=response_body)
            c.sendall(p.encode())

        c.close()
    except KeyboardInterrupt:
        break

print("\nClosing")