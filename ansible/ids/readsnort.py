#!/usr/bin/env python3
"""Run snort and print each alert as soon as it is generated using Unix domain sockets."""
import ctypes
import os
import socket
from datetime import datetime
from subprocess import Popen
from snort import Alertpkt

# listen for alerts using unix domain sockets (UDS)
UNSOCK_FILE = 'snort_alert'
snort_log_dir = '/var/log/snort'
server_address = os.path.join(snort_log_dir, UNSOCK_FILE)

sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
try:
    os.remove(server_address)
except OSError:
    pass
sock.bind(server_address)

## start snort process
#snort_process = Popen(['snort', '-A', 'unsock', '-l', snort_log_dir, '-c', '/etc/snort/snort.conf', '-Q', '-i', 'enp0s9:enp0s10', '--daq', 'afpacket', '--daq-mode', 'inline'], close_fds=True)

# receive alerts
alert = Alertpkt()
try:
    while 1:
        if sock.recv_into(alert) != ctypes.sizeof(alert):
            break # EOF
        #run python script here `subprocess.call([sys.executable or 'python', '-m', 'your_module'])`
        #print("{:03d} {:%H:%M:%S}".format(alert.val, datetime.fromtimestamp(alert.data)))
        print(alert.getMessage())
except KeyboardInterrupt:
    pass
finally:
    sock.close()
    os.remove(server_address)
