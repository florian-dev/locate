import string, subprocess, os, tempfile, random, time
from ctypes import windll

def _logical_drives():
	drives = []
	bitmask = windll.kernel32.GetLogicalDrives()
	for letter in string.uppercase:
		if bitmask & 1:
			drives.append(letter)
		bitmask >>= 1
	return drives

def _free_drive():
	drives = _logical_drives()
	for letter in sorted(string.uppercase, reverse=True):
		if letter not in drives: return letter
	return None

def _write_random_file(path):
	chars = string.lowercase + ' '
	with open(path+'.txt', 'w') as file:
		nb_lines = random.randint(1, 200)
		for l in xrange(nb_lines):
			nb_chars = random.randint(10, 200)
			for c in xrange(nb_chars):
				file.write(random.choice(chars))
			file.write('\n')

def _remove_dir(path):
	files = os.listdir(path)
	if files:
		for file in files:
			fullpath = os.path.join(path, file)
			if os.path.isdir(fullpath):
				_remove_dir(fullpath)
			else:
				os.remove(fullpath)
	os.rmdir(path)
	
def write_tree(path, max_depth=0, max_files=12, proba_files=.7, max_dirs=3, proba_dirs=.3):
	path_list = [p for p in path.split(';') if p]
	types = dict()
	types['file'] = proba_files, max_files, _write_random_file
	if max_depth > 0: types['dir'] = proba_dirs, max_dirs, os.mkdir
	dirs = []
	for key in types.iterkeys():
		proba, max, func = types[key]
		if random.random() < proba:
			nb_files = random.randrange(max) + 1
			suff_len = str(len(str(nb_files)))
			for i in xrange(nb_files):
				filename = ('{}_{}{:0>'+suff_len+'}').format(key, int(time.time()*1000), i+1)
				for p in path_list:
					fullpath = os.path.join(p, filename)
					func(fullpath)
					if key == 'dir': dirs.append(fullpath)
	for dir in dirs:
		write_tree(dir, max_depth-1, max_files, proba_files, max_dirs, proba_dirs)

def make_drive():
	tmp_dir = tempfile.mkdtemp()
	drive = _free_drive()
	subprocess.check_call(['subst', drive+':', tmp_dir])
	return drive, tmp_dir

def del_drive(drive, tmp_dir):
	subprocess.check_call(['subst', drive+':', '/d'])
	_remove_dir(tmp_dir)
	
def touch(files, prefix='./'):
	if isinstance(files, basestring): files = [files]
	for file in files:
		path = os.path.join(prefix, file)
		dir, filename = os.path.split(path)
		if not os.path.exists(dir):
			os.makedirs(dir)
		with open(path, 'a') as f:
			pass
