# -*- coding: utf8 -*-

import sys, codecs, textwrap
from os.path import join, expanduser
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
	if args.func == updatedb and args.clean_drives:
		for drive in args.clean_drives:
			db.clear(drive)
	_updatedb(db, args)
	if args.quiet < 1: _size_not_found_report(db)
	_savedb(db, args.quiet < 2)
	if args.func == updatedb and args.repport:
		_repport(db)
	
def find(db, args):
	drives = args.drives
	if args.exclude_drives:
		if drives is None: drives = db.drives()
		drives = [drive for drive in drives if drive not in args.exclude_drives]
	matches = db.find(args.pattern, args.ignore_case)
	matches.sort()
	for root, file, size in matches:
		if size < args.file_size_threshold: continue
		if not drives is None and root[0].upper() not in drives: continue
		print join(root, file), '(', hr_size(size), ')'
		
general_options_parser = argparse.ArgumentParser(add_help=False)
general_options = general_options_parser.add_argument_group('general options')
general_options.add_argument('-p', '--db-filepath', type=args_types.file_path, default='~/files_db_default_file.db', metavar='<path>', help='files database file path')
general_options.add_argument('-d', '--drives', type=args_types.drives_letters, metavar='<drives>',
	help='restrict action to some drives')
general_options.add_argument('-x', '--exclude-drives', type=args_types.drives_letters, nargs='?', const='', default='C', metavar='<drives>',
	help='do not update or use data for these drives')
general_options.add_argument('-u', '--updatedb', action='store_true',
	help='update files database before processing')
general_options.add_argument('-l', '--log-file', type=args_types.opened_log_file, metavar='<log_file>',
	help="use %(metavar)s as main output with utf8 encoding and convert stdout to 'replace' mode if --no-stdout is not present")
general_options.add_argument('-n', '--no-stdout', action='store_true')
general_options.add_argument('-q', '--quiet', action='count', default=0)

parser = argparse.ArgumentParser(description='locate files in a managed database')
subparsers = parser.add_subparsers(title='commands')

syntax_strings = {	'drives': "<drives>    : (<letter>[:])+        Example: 'dE:h:Gp'",
					'file_size': "<file_size> : <integer>[kMGT][B]    Example: '500kB'" }
description_strings = {	'find': 'find files in database',
						'updatedb': 'update database',
						'duplicates': 'find duplicate files in database' }
formatter_class_combo = type('combo', (argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter), dict())

cmd = 'find'
parser_find = subparsers.add_parser(cmd, usage='%(prog)s [options] pattern', parents=[general_options_parser], add_help=False,
	formatter_class=formatter_class_combo, epilog='\n'.join(syntax_strings.itervalues()),
	help=description_strings[cmd], description=description_strings[cmd])
parser_find.add_argument('pattern', help="filname pattern to search for ; pattern can contain '*' to widen results")
find_options = parser_find.add_argument_group('find options')
find_options.add_argument('-h', '--help', action='help', help='show this help message and exit')
find_options.add_argument('-i', '--ignore-case', action='store_true')
find_options.add_argument('-t', '--file-size-threshold', type=args_types.file_size, default=0, metavar='<file_size>',
	help='file size threshold (smaller ones are ignored)')
parser_find.set_defaults(func=find)

cmd = 'updatedb'
parser_updatedb = subparsers.add_parser(cmd, usage='%(prog)s [options]', parents=[general_options_parser], add_help=False,
	formatter_class=formatter_class_combo, epilog=syntax_strings['drives'],
	help=description_strings[cmd], description=description_strings[cmd])
updatedb_options = parser_updatedb.add_argument_group('updatedb options')
updatedb_options.add_argument('-h', '--help', action='help', help='show this help message and exit')
updatedb_options.add_argument('-r', '--repport', action='store_true',
	help='print database repport')
updatedb_options.add_argument('-c', '--clean-drives', type=args_types.drives_letters, metavar='<drives>',
	help='clean data for these drives (before update)')
parser_updatedb.set_defaults(func=updatedb)

cmd = 'duplicates'
parser_duplicates = subparsers.add_parser(cmd, usage='%(prog)s [options]', parents=[general_options_parser], add_help=False,
	formatter_class=formatter_class_combo, epilog='\n'.join(syntax_strings.itervalues()),
	help=description_strings[cmd], description=description_strings[cmd])
duplicates_options = parser_duplicates.add_argument_group('duplicates options')
duplicates_options.add_argument('-h', '--help', action='help', help='show this help message and exit')
duplicates_options.add_argument('-s', '--sort-criteria', choices=['file','directory'], default='file',
	help="sort criteria : 'file' (default) = by decreasing file count ; 'directory' = by decreasing directories count, then by directories names")
duplicates_options.add_argument('-v', '--view-max-file-count', type=int, nargs='?', const=15, default=-1, metavar='<count>',
	help='print only first %(metavar)s file(s) per result (implicit value: %(const)s)')
filter_options = parser_duplicates.add_argument_group('filters', description=textwrap.dedent('''\
	filter  1 :  ignore results with more than three files and whose all
	             filenames are same except for digits characters (0-9)
	'''))
filter_options.add_argument('-f', '--filter', action='append', type=int, choices=[1],
	help='apply one filter among those listed above ; this option can be mentioned several times')
filter_options.add_argument('-t', '--file-size-threshold', type=args_types.file_size, nargs='?', const='2MB', default=0, metavar='<file_size>',
	help='file size threshold (smaller ones are ignored) (implicit value: %(const)s)')
filter_options.add_argument('-m', '--min-file-count', type=int, nargs='?', const=6, default=1, metavar='<count>',
	help='exclude results with less than %(metavar)s duplicate files (implicit value: %(const)s)')
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
if args.drives and args.exclude_drives: args.drives = [drive for drive in args.drives if drive not in args.exclude_drives]
_loaddb(db, args.quiet < 2)
if args.updatedb and args.func != updatedb: updatedb(db, args)
if args.quiet < 2: print

args.func(db, args)
