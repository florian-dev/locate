# -*- coding: utf8 -*-
import os, sys, pickle, codecs
from os.path import join, abspath, dirname
from time import time
import tee
import files_db
import argparse

def _hr_size(size): # -> human readable file size (ex: '698.43 MB')
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
		
def _loaddb(db, verbose=False):
	if verbose:
		print 'loading database ...',
		t = time()
	c = db.load()
	if verbose:
		t = round(time()-t, 1)
		print '{} file entries loaded in {} s'.format(c, t)

def _savedb(db, verbose=False):
	if verbose:
		print 'saving database ...',
	t = time()
	success = db.save()
	t = round(time()-t, 1)
	if not success:
		print 'error - Data NOT saved ! ({} s)'.format(t)
	elif verbose:
		c = len(db)
		print '{} file entries saved in {} s'.format(c, t)

def _size_not_found_report(db):
	if db.size_not_found:
		db.size_not_found.sort()
		print 'file scan failed to read size of following files (stored size: 0) :'
		print
		for path in db.size_not_found:
			print path
		print

def _updatedb(db, quiet):
	if quiet < 2: print 'updating files database ...',
	t0 = time()
	if quiet < 1:
		print
		c = 0
		s = 0
		t = t0
		for root, file, size in db.update_gen():
			c += 1
			s += size
			if time() - t > 2:
				print u' {:<12} {}'.format(_hr_size(s), root)
				t = time()
	else: c = db.update()
	if quiet < 2: print '{} files updated in {} s'.format(c, round(time() - t0, 2))
	
def _repport_total_size(db):
	drives = db.drives()
	if drives:
		msg = '{} in '.format(_hr_size(db.size()))
		c = len(drives)
		if c > 1: msg += '{} drives.'.format(c)
		else: msg += 'drive {}.'.format(drives[0])
		print msg
	else: print 'database is empty.'

def updatedb(db, args):
	_updatedb(db, args.quiet)
	if args.quiet < 1: _size_not_found_report(db)
	_savedb(db, args.quiet < 2)
	if args.func == updatedb and args.repport_total_size:
		_repport_total_size(db)
	
def find(db, args):
	matches = db.find(args.pattern, args.ignore_case)
	matches.sort()
	for root, file, size in matches:
		print join(root, file), '(', _hr_size(size), ')'

def duplicates(db, args):
	verbose = args.quiet < 2
	all_files = sorted(db.files(), key=lambda item: item[1])
	c_all = len(all_files)
		
	seuil = args.file_size_threshold
	files_by_name = []
	while all_files:
		root, file, size = all_files.pop()
		if seuil and size < seuil: continue
		if files_by_name and file.lower() == files_by_name[-1][0].lower():
			files_by_name[-1][1].append((root, size))
		else:
			files_by_name.append(( file, [ (root, size) ] ))

	if verbose and seuil: print 'Files smaller than', _hr_size(seuil), 'are ignored.'
	if verbose: print 'Count of filenames :', len(files_by_name)

	doublons = []
	while files_by_name:
		file, r_s = files_by_name.pop()
		if len(r_s) > 1:
			r_s.sort(key=lambda item: item[0], reverse=True)
			roots, sizes = [], []
			while r_s:
				root, size = r_s.pop()
				roots.append(root)
				sizes.append(size)
			doublons.append((file, roots, sizes))

	if not doublons:
		if verbose: print 'Aucun doublon trouve.'
	else:
		doublons.sort(key=lambda item:item[1])
		if verbose: print 'Noms de fichiers non uniques :', len(doublons)

		doublons_par_reps = []
		while doublons:
			file, roots, sizes = doublons.pop()
			if doublons_par_reps and roots == doublons_par_reps[-1][0]:
				doublons_par_reps[-1][1].append(file)
			else:
				doublons_par_reps.append(( roots, [ file ] ))
		if verbose: print u'Tuples de répertoires contenant des fichiers de même nom :', len(doublons_par_reps)
		
		seuil = args.min_file_count
		if seuil > 1:
			doublons_par_reps2 = []
			while doublons_par_reps:
				doublon = doublons_par_reps.pop()
				if len(doublon[1]) >= seuil:
					doublons_par_reps2.append(doublon)
			doublons_par_reps = doublons_par_reps2
			if verbose: print u'Tuples de répertoires contenant plus de', seuil, u'fichiers de même nom :', len(doublons_par_reps)
			
		# filtre 1 : enlève les résultats contenant plus de trois fichiers et dont les noms de fichiers (tous)
		#            sont identiques à l'exception des éventuels caractères numériques (0-9)
		if args.filter_01:
			def grey_digits(string):
				grey_str = string
				for digit in '0123456789':
					if digit in grey_str:
						grey_str = grey_str.replace(digit, '*')
				return grey_str
			if verbose: print 'Application du filtre 1 ...',
			doublons_par_reps2 = []
			while doublons_par_reps:
				doublon = doublons_par_reps.pop()
				if len(doublon[1]) > 3:
					str_cmp = grey_digits(doublon[1][0])
					exclude = True
					for i in xrange(1, len(doublon[1])):
						if grey_digits(doublon[1][i]) != str_cmp:
							exclude = False
							break
					if exclude: continue
				doublons_par_reps2.append(doublon)
			doublons_par_reps = doublons_par_reps2
			if verbose: print 'tuples restants :', len(doublons_par_reps)
			
		if verbose: print

		if args.directory_sorting:
			# tri par nombre de repertoires concernes (decroissant) puis alphabetique par répertoires
			# (-len(t), '*'.join([s[0] for s in t] + t))
			doublons_par_reps2 = []
			while doublons_par_reps:
				doublon = doublons_par_reps.pop()
				roots = doublon[0]
				cmp_str = ''
				c = max([len(s) for s in roots])
				for i in xrange(c):
					for root in roots:
						if i < len(root):
							cmp_str += root[i]
				cmp_tuple = -len(roots), cmp_str
				doublons_par_reps2.append((doublon, cmp_tuple))
			doublons_par_reps2.sort(key=lambda item: item[1], reverse=True)
			while doublons_par_reps2:
				doublons_par_reps.append(doublons_par_reps2.pop()[0])
		else:
			# tri par nombre de resultats decroissant
			doublons_par_reps.sort(key=lambda item:(-len(item[1]), item[0]))

		for doublon in doublons_par_reps:
			for root in doublon[0]:
				print root
			print len(doublon[1]), 'fichiers en commun',
			if args.view_max_file_count != 0:
				print ':'
				print
				doublon[1].sort()
				i = 0
				for file in doublon[1]:
					if i == args.view_max_file_count:
						print '  ...'
						break
					print u'  {}'.format(file)
					i += 1
			else: print '.'
			print
			
class fake_fd:
	def write(self, text): pass
	def flush(self): pass

def opened_log_file(filename):
	mode, encoding = 'w', 'utf8'
	try:
		log_fd = codecs.open(filename, mode, encoding)
		return log_fd
	except:
		msg = 'An error occured while opening "{}" (mode=\'{}\', encoding=\'{}\') !'.format(filename, mode, encoding)
		raise argparse.ArgumentTypeError(msg)

def try_int(value_str): # -> success, value
	success = True
	try:
		value = int(value_str)
	except:
		success = False
		value = None
	return success, value
	
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

def file_size(value_str):
	msg = ''
	if value_str[-1] == 'B': value_str = value_str[:-1]
	mult = 1
	mults = ('k','M','G','T')
	if value_str and value_str[-1] in mults:
		mult = 1024**( mults.index(value_str[-1]) + 1 )
		value_str = value_str[:-1]
	if value_str:
		success, value = try_int(value_str)
		if success:
			if value >= 0: return value * mult
			else: msg = 'Negative values are not allowed !'
		else: msg = "'{}' is not an integer !".format(value_str)
	else: msg = '<size> is empty !'.format(value_str)
	raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser(description='locate files in a managed database')
parser.add_argument('-d', '--db-filepath', type=file_path, default='c:/files.db', metavar='<path>', help='files database file path')
parser.add_argument('-u', '--updatedb', action='store_true',
	help='update files database before processing')
parser.add_argument('-l', '--log-file', type=opened_log_file, metavar='<log_file>',
	help="use %(metavar)s as main output with utf8 encoding and convert stdout to 'replace' mode if --no-stdout is not present.")
parser.add_argument('-n', '--no-stdout', action='store_true')
parser.add_argument('-q', '--quiet', action='count', default=0)

subparsers = parser.add_subparsers()

parser_find = subparsers.add_parser('find', help='find files in database')
parser_find.add_argument('pattern')
parser_find.add_argument('-i', '--ignore-case', action='store_true')
parser_find.set_defaults(func=find)

parser_updatedb = subparsers.add_parser('updatedb', help='update database')
parser_updatedb.add_argument('-r', '--repport-total-size', action='store_true',
	help='print sum of all files size in database')
parser_updatedb.set_defaults(func=updatedb)

parser_duplicates = subparsers.add_parser('duplicates', help='find duplicate files in database')
parser_duplicates.add_argument('-t', '--file-size-threshold', type=file_size, nargs='?', const='2MB', default=0, metavar='<file_size>',
	help="File size threshold (smaller ones are ignored). %(metavar)s syntax is '<integer>[kMGT][B]'. Example: '500kB' (default: %(const)s)")
parser_duplicates.add_argument('-d', '--directory-sorting', action='store_true',
	help='Sort by decreasing directories count, then by directories names. Default sort is by decreasing file count.')
parser_duplicates.add_argument('-m', '--min-file-count', type=int, nargs='?', const=6, default=1, metavar='<count>',
	help='Exclude results with less than %(metavar)s duplicate files. (default: %(const)s)')
parser_duplicates.add_argument('-v', '--view-max-file-count', type=int, nargs='?', const=15, default=-1, metavar='<count>',
	help='Print only first %(metavar)s file(s) per result. (default: %(const)s)')
parser_duplicates.add_argument('-f', '--filter-01', action='store_true',
	help='filter 1 : ignore results with more than three files and whose all filenames are same except for digits characters (0-9)')
parser_duplicates.set_defaults(func=duplicates)

args = parser.parse_args()

# log option
if args.log_file:
	if args.no_stdout:
		sys.stdout = args.log_file
	else:
		sys.stdout = tee.tee(
				codecs.getwriter(sys.stdout.encoding)(sys.stdout, 'replace'),
				args.log_file
				)
elif args.no_stdout: sys.stdout = fake_fd()

db = files_db.FilesDb(exclude_drives=('C','D','P'), db_filepath=args.db_filepath)
_loaddb(db, args.quiet < 2)
if args.updatedb and args.func != updatedb: updatedb(db, args)
if args.quiet < 2: print

args.func(db, args)
