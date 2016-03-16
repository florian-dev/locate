# -*- coding: utf8 -*-

import argparse, os, codecs

def opened_log_file(filename):
	mode, encoding = 'w', 'utf8'
	try:
		log_fd = codecs.open(filename, mode, encoding)
		return log_fd
	except:
		msg = 'An error occured while opening "{}" (mode=\'{}\', encoding=\'{}\') !'.format(filename, mode, encoding)
		raise argparse.ArgumentTypeError(msg)

def _try_int(value_str): # -> success, value
	success = True
	try:
		value = int(value_str)
	except:
		success = False
		value = None
	return success, value

def file_size(value_str):
	msg = ''
	if value_str[-1] == 'B': value_str = value_str[:-1]
	mult = 1
	mults = ('k','M','G','T')
	if value_str and value_str[-1] in mults:
		mult = 1024**( mults.index(value_str[-1]) + 1 )
		value_str = value_str[:-1]
	if value_str:
		success, value = _try_int(value_str)
		if success:
			if value >= 0: return value * mult
			else: msg = 'Negative values are not allowed !'
		else: msg = "'{}' is not an integer !".format(value_str)
	else: msg = '<size> is empty !'.format(value_str)
	raise argparse.ArgumentTypeError(msg)
	
def _check_drive(letter):
	if ord(letter) not in range(ord('A'), ord('Z')+1):
		raise argparse.ArgumentTypeError("'{}' is not a drive letter".format(letter))

def drives_letters(drives_str):
	drives = drives_str[0].upper()
	if len(drives_str) > 1: drives += drives_str[1:].replace(':', '').upper()
	for drive in drives:
		_check_drive(drive)
	return drives
	
def drive(drive_str):
	if len(drive_str) == 1 or (len(drive_str) == 2 and drive_str[1] == ':'):
		letter = drive_str[0].upper()
	else:
		raise argparse.ArgumentTypeError("'{}' is too long to be a drive letter".format(drive_str))
	_check_drive(letter)
	return letter

def file_path(path):
	ok = True
	if os.access(path, os.F_OK):
		if not os.access(path, os.R_OK | os.W_OK):
			ok = False
	else:
		try:
			f = open(path, 'w')
			f.close()
			os.remove(path)
		except:
			ok = False
	if ok: return path
	else: raise argparse.ArgumentTypeError(path + ' : Access denied !')

