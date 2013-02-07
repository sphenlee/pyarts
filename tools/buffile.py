'''
buffile

Treat a buffer as a file
'''

import os

class Buffile(object):
    def __init__(self, buf):
        self.buf = buf
        self.pos = 0

    def seek(self, off, whence=os.SEEK_SET):
        if whence == os.SEEK_SET:
            self.pos = off
        elif whence == os.SEEK_CUR:
            self.pos += off
        elif whence == os.SEEK_END:
            self.pos = len(self.buf) - off

    def read(self, n=None):
        if n is None:
            self.pos = len(self.buf)
            return str(self.buf)
        else:
            s = str(self.buf[self.pos:self.pos + n])
            self.pos += n
            return s
