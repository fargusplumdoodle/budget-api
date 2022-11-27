import socket
import sys


for spec in sys.argv[1:]:
    host, port = spec.split(":", maxsplit=1)
    sock = socket.socket(socket.AF_INET)
    sock.settimeout(1)

    try:
        sock.connect((host, int(port)))
        sock.close()
    except (socket.timeout, ConnectionError):
        sys.exit(1)

sys.exit(0)
