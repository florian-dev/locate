# -*- coding: utf8 -*-

from common import hr_size
import itertools, string
from collections import Counter

def _files_gen(db, drives, exclude_drives):
	if drives is None: drives = db.drives()
	if exclude_drives: drives = [drive for drive in drives if drive not in exclude_drives]
	return itertools.chain.from_iterable(itertools.imap(db.files, drives))
	#for drive in drives:
	#	for file in db.files(drive):
	#		yield file

def duplicates(db, args, ignore_case=True, check_exact_filesize=False):
	r"""
	>>> args_d = dict(quiet = 2, drives = testdb.drives(), exclude_drives = None, file_size_threshold = 0,
	... 	min_file_count = 1, filter = [1], sort_criteria = 'file', view_max_file_count = -1,
	... 	ignore_case=True, check_exact_filesize=False, check_approximative_filesize=False )
	>>> args = argparse.Namespace(**args_d)
	>>> duplicates(testdb, args)
	Y:\2_Et\sangloter\d'extase les\jets\d'eau,
	Y:\3_Les grands jets\d'eau sveltes\parmi les marbres
	Z:\0_Au calme\clair de lune\triste\et\beau,
	Z:\1_Qui fait\rEver les oiseaux\dans les\arbres
	1 fichiers en commun :
	<BLANKLINE>
	  blank.w
	<BLANKLINE>
	>>> args.ignore_case = False
	>>> args.check_exact_filesize = True
	>>> duplicates(testdb, args)
	Y:\2_Et\sangloter\d'extase les\jets\d'eau,
	Y:\3_Les grands jets\d'eau sveltes\parmi les marbres
	1 fichiers en commun :
	<BLANKLINE>
	  Blank.w
	<BLANKLINE>
	Z:\0_Au calme\clair de lune\triste\et\beau,
	Z:\1_Qui fait\rEver les oiseaux\dans les\arbres
	1 fichiers en commun :
	<BLANKLINE>
	  blank.w
	<BLANKLINE>
	"""
	all_files = _files_gen(db, args.drives, args.exclude_drives)
	verbose = args.quiet < 2
		
	# file_size_threshold
	seuil = args.file_size_threshold
	if seuil > 0:
		func = lambda (root, file, size): size >= seuil
		all_files = itertools.ifilter(func, all_files)
		if verbose: print 'Files smaller than', hr_size(seuil), 'are ignored.'
	
	# ignore case
	if args.ignore_case:
		ignore_case_func = lambda (root, file, size): (root, file.lower(), size)
		if verbose: print 'Ignore case : On'
	else: ignore_case_func = lambda i:i
	
	# check exact filesize
	if args.check_exact_filesize:
		select_func = lambda (root, file, size): (file, size)
		if verbose: print 'Check exact filesize : On'
	else: select_func = lambda (root, file, size): (file,)
	
	group_key = lambda file: select_func(ignore_case_func(file))
	
	all_files = sorted(all_files, key=group_key)
	c_all = len(all_files)
	
	doublons = []
	filenames_count = 0
	duplicates_filenames_count = 0
	duplicates_count = 0
	for k, g in itertools.groupby(all_files, group_key):
		filenames_count += 1
		r_s = map(lambda (root, file, size): (root, size), g)
		if len(r_s) > 1:
			duplicates_filenames_count += 1
			# check_approximative_filesize
			if args.check_approximative_filesize:
				sizes = [size for root, size in r_s]
				average = float(sum(sizes)) / len(sizes)
				cinq_pc = average * .05
				min = average - cinq_pc
				max = average + cinq_pc
				r_s = filter(lambda (root, size): min <= size <= max, r_s)
				if len(r_s) <= 1: continue
			duplicates_count += 1
			doublon = tuple([k[0]] + zip(*r_s))
			doublons.append(doublon)
	del all_files
		
	if verbose:
		print 'Count of filenames :', filenames_count
		if filenames_count:
			if duplicates_count != duplicates_filenames_count:
				print 'Duplicates filenames count :', duplicates_filenames_count
			print 'Duplicates files group count :', duplicates_count
	
	if duplicates_filenames_count == 0:
		if verbose: print 'Aucun doublon trouve.'
		return
		
	# min_file_count
	seuil = args.min_file_count
	
	# group by roots
	group_key = lambda (file, roots, sizes): roots
	doublons.sort(key=group_key)
	doublons_par_reps = []
	directory_tuples_count = 0
	final_directory_tuples_count = 0
	for k, g in itertools.groupby(doublons, group_key):
		directory_tuples_count += 1
		files = map(lambda (file, roots, sizes): file, g)
		if seuil < 2 or len(files) >= seuil:
			final_directory_tuples_count += 1
			doublons_par_reps.append((k, files))
	del doublons
	
	if verbose:
		print 'Count of directory groups :', directory_tuples_count
		if directory_tuples_count != final_directory_tuples_count:
			print 'Count of directory groups with', seuil, 'duplicates files or more :', final_directory_tuples_count
	
	# filters
	if args.filter:
		def remove_digits(str):
			grey_str = str
			for digit in string.digits:
				if digit in grey_str:
					grey_str = grey_str.replace(digit, '')
			return grey_str
		def filter_nmax_files(n):
			return lambda (roots, files): len(files) <= n
		def filter_key2(doublon):
			roots, files = doublon
			c = len(Counter(itertools.imap(remove_digits, files)))
			return c != 1
		
		# filtre 1 : enlève les résultats contenant plus de trois fichiers et dont les noms de fichiers (tous)
		#            sont identiques à l'exception des éventuels caractères numériques (0-9)
		if 1 in args.filter and 2 not in args.filter:
			filter_key = lambda doublon: filter_nmax_files(3)(doublon) or filter_key2(doublon)
			if verbose: print 'Application du filtre 1 ...',
			doublons_par_reps = filter(filter_key, doublons_par_reps)
			if verbose: print 'tuples restants :', len(doublons_par_reps)
		
		# filtre 2 : enlève les résultats dont les noms de fichiers sont identiques
		#            à l'exception des éventuels caractères numériques (0-9)
		if 2 in args.filter or 3 in args.filter:
			f = 2
			# filtre 3 : comme le 2 mais commence par remplacer /[ _-]+/ par ' '
			if 3 in args.filter:
				f = 3
				import re
				def inner_strip(doublon):
					roots, files = doublon
					regx = re.compile(r'[ _-]+')
					return roots, [regx.sub(' ', file) for file in files]
				filter_key3 = inner_strip
			else: filter_key3 = lambda i:i
			filter_key = lambda doublon: filter_nmax_files(1)(doublon) or filter_key2(filter_key3(doublon))
			if verbose: print 'Application du filtre {} ...'.format(f),
			doublons_par_reps = filter(filter_key, doublons_par_reps)
			if verbose: print 'tuples restants :', len(doublons_par_reps)
		
	if args.sort_criteria == 'directory':
		# tri par nombre de repertoires concernes (decroissant) puis alphabetique par répertoires
		# (-len(t), '*'.join([s[0] for s in t] + t))
		sort_key = lambda (roots, files): (-len(roots), map(''.join, itertools.izip_longest(*roots, fillvalue='')))
		doublons_par_reps.sort(key=sort_key)
	elif args.sort_criteria == 'file':
		# tri par nombre de resultats decroissant
		doublons_par_reps.sort(key=lambda item:(-len(item[1]), item[0]))

	if verbose: print

	for roots, files in doublons_par_reps:
		for root in roots:
			print root
		print len(files), 'fichiers en commun',
		if args.view_max_file_count != 0:
			print ':'
			print
			files.sort()
			i = 0
			for file in files:
				if i == args.view_max_file_count:
					print '  ...'
					break
				print u'  {}'.format(file)
				i += 1
		else: print '.'
		print
			
if __name__ == '__main__':
	import doctest, argparse
	from files_db import FilesDb
	import files_db_test as test
	drives, updated_db, sav = test.duplicates_context_build(FilesDb())
	doctest.testmod(
		name='duplicates',
		extraglobs=dict(drive1=drives[0], drive2=drives[1], testdb=updated_db),
		optionflags=doctest.REPORT_ONLY_FIRST_FAILURE
		)
	test.context_del(drives, sav)
