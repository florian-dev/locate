# -*- coding: utf8 -*-

import sys, codecs
from os.path import join
from time import time
import argparse
import tee, files_db, args_types
from common import *
from duplicates import duplicates

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

def _update_gen(db, drives):
	if drives is None:
		for file in db.update_gen():
			yield file
	else:
		for file in db.update_drives_gen(drives):
			yield file

def _updatedb(db, args):
	if args.quiet < 2: print 'updating files database ...',
	t0 = time()
	if args.quiet < 1:
		print
		c = 0
		s = 0
		t = t0
		for root, file, size in _update_gen(db, args.drives):
			c += 1
			s += size
			if time() - t > 2:
				print u' {:<12} {}'.format(hr_size(s), root)
				t = time()
	else:
		if args.drives is None: c = db.update()
		else: c = db.update_drives(args.drives)
	if args.quiet < 2: print '{} files updated in {} s'.format(c, round(time() - t0, 2))
	
def _repport(db):
	drives = db.drives()
	if drives:
		header_str = '{:^9}|{:^13}|{:^16}'
		separa_str = '{:-<9}+{:-<13}+{:-<16}'.format('','','')
		values_str = '{:^9}|{:^13}|{:>15,}'
		print header_str.format('Drive', 'Size', 'File count')
		print separa_str
		dc = 0 # drive count
		ts = 0 # total size
		tfc = 0 # total file count
		for drive in drives:
			s = db.size(drive)
			ts += s
			fc = db.len(drive)
			tfc += fc
			print values_str.format(drive, hr_size(s), fc)
			dc += 1
		if dc > 1:
			print separa_str
			print values_str.format('All {}'.format(dc), hr_size(ts), tfc)
	else: print 'database is empty.'

def updatedb(db, args):
	_updatedb(db, args)
	if args.quiet < 1: _size_not_found_report(db)
	_savedb(db, args.quiet < 2)
	if args.func == updatedb and args.repport:
		_repport(db)
	
def find(db, args):
	matches = db.find(args.pattern, args.ignore_case)
	matches.sort()
	for root, file, size in matches:
		if root[0].upper() not in args.drives: continue
		print join(root, file), '(', hr_size(size), ')'
		
parser = argparse.ArgumentParser(description='locate files in a managed database')
parser.add_argument('-d', '--db-filepath', type=args_types.file_path, default='c:/files.db', metavar='<path>', help='files database file path')
parser.add_argument('--drives', type=args_types.drives_letters, metavar='<drives>',
	help="restrict action to some drives (ex: '--drives dE:h:Gp') ('x:' = 'x' = 'X' = 'X:')")
parser.add_argument('-x', '--exclude-drives', type=args_types.drives_letters, nargs='?', const='', default='C', metavar='<drives>',
	help="do not update data for these drives (default: %(default)s)")
parser.add_argument('-u', '--updatedb', action='store_true',
	help='update files database before processing')
parser.add_argument('-l', '--log-file', type=args_types.opened_log_file, metavar='<log_file>',
	help="use %(metavar)s as main output with utf8 encoding and convert stdout to 'replace' mode if --no-stdout is not present.")
parser.add_argument('-n', '--no-stdout', action='store_true')
parser.add_argument('-q', '--quiet', action='count', default=0)

subparsers = parser.add_subparsers()

parser_find = subparsers.add_parser('find', help='find files in database')
parser_find.add_argument('pattern')
parser_find.add_argument('-i', '--ignore-case', action='store_true')
parser_find.set_defaults(func=find)

parser_updatedb = subparsers.add_parser('updatedb', help='update database')
parser_updatedb.add_argument('-r', '--repport', action='store_true',
	help='print database repport')
parser_updatedb.set_defaults(func=updatedb)

parser_duplicates = subparsers.add_parser('duplicates', help='find duplicate files in database')
parser_duplicates.add_argument('-t', '--file-size-threshold', type=args_types.file_size, nargs='?', const='2MB', default=0, metavar='<file_size>',
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

db = files_db.FilesDb(exclude_drives=args.exclude_drives, db_filepath=args.db_filepath)
if args.drives is None: args.drives = db.drives()
if args.exclude_drives: args.drives = [drive for drive in args.drives if drive not in args.exclude_drives]
_loaddb(db, args.quiet < 2)
if args.updatedb and args.func != updatedb: updatedb(db, args)
if args.quiet < 2: print

args.func(db, args)
