# -*-coding:Utf-8 -*
import sys

class tee :
    def __init__(self, _fd1, _fd2) :
        self.fd1 = _fd1
        self.fd2 = _fd2

    def __del__(self) :
        if self.fd1 != sys.stdout and self.fd1 != sys.stderr :
            self.fd1.close()
        if self.fd2 != sys.stdout and self.fd2 != sys.stderr :
            self.fd2.close()

    def write(self, text) :
		self.fd1.write(text)
		self.fd2.write(text)

    def flush(self) :
        self.fd1.flush()
        self.fd2.flush()

# usage :
#
#import codecs
#
#def tee_out(filename):
#	fd = sys.stdout
#	output = open(filename, "w")
#	sys.stdout = tee(fd, output)
#	return fd
#
#def tee_out_utf8(filename):
#	fd = sys.stdout
#	output = codecs.open(filename, 'w', 'utf8')
#	sys.stdout = tee(fd, output)
#	return fd
#
#def untee_out(fd):
#	sys.stdout = fd
