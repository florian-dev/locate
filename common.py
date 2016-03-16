# -*- coding: utf8 -*-

class fake_fd:
	def write(self, text): pass
	def flush(self): pass

def hr_size(size): # -> human readable file size (ex: '698.43 MB')
	if size < 900:
		if size > 1: plural = 's'
		else: plural = ''
		return '{} byte{}'.format(size, plural)
	f = 1024.
	s = size / f
	mults = [ 'k', 'M', 'G', 'T' ]
	i = 0
	while i < 3 and s > 900:
		s /= f
		i += 1
	return '{:.2f} {}B'.format(s, mults[i])
