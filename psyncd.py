#!/usr/bin/env python
#encoding=utf-8
"""
p-syncd
"""
import os
import sys
import optparse
import socket
import threading

def process_command_line(argv):
    if argv is None:
        argv = sys.argv[1:]

    parser = optparse.OptionParser(
        formatter=optparse.TitledHelpFormatter(width=78),
        add_help_option=None)

    parser.add_option(
        '-h', '--help', action='help',
        help='help')

    parser.add_option('-p', '--port', dest="port", type="int", default=17159)

    settings, args = parser.parse_args(argv)

    if args:
        parser.error('program takes no command-line arguments; '
                     '"%s" ignored.' % (args,))

    return settings, args

def open_file(filename, desc = 'w'):
    dirname, _ = os.path.split(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return open(filename, desc)

def connection_handler(sock):
    fp = sock.makefile()
    ctl_line = fp.readline()
    args = ctl_line.split() 
    # FILE filename offset size
    cmd = args[0].upper()
    if cmd == 'FILE':
        file_name = args[1]
        size = int(args[2])
        mode = int(args[3])
        # read buf
        buf = fp.read(size)
        while len(buf) < size:
            buf += fp.read(size - len(buf))
        assert len(buf) == size
        # write to file
        localfp = open_file(file_name)
        localfp.write(buf)
        localfp.close()

        os.chmod(file_name, mode)
        fp.write('DONE\r\n')
        fp.flush()
    fp.close()
    sock.close()

def main(argv=None):
    settings, args = process_command_line(argv)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', settings.port))       
    sock.listen(5)
    while True:
        client, addr = sock.accept()
        t = threading.Thread(target = connection_handler,
                             args=(client, ))
        t.start() 
    return 0

if __name__ == '__main__':
    try:
        status = main()
        sys.exit(status)
    except KeyboardInterrupt:
        sys.exit(0)