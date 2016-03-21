# -*- coding: utf8 -*-

from common import hr_size
import itertools

def _files_gen(db, drives, exclude_drives):
	if drives is None: drives = db.drives()
	if exclude_drives: drives = [drive for drive in drives if drive not in exclude_drives]
	return itertools.chain.from_iterable(itertools.imap(db.files, drives))
	#for drive in drives:
	#	for file in db.files(drive):
	#		yield file

def duplicates(db, args, ignore_case=True):
	r"""
	>>> args_d = dict(quiet = 2, drives = testdb.drives(), exclude_drives = None, file_size_threshold = 0,
	... 	min_file_count = 1, filter = None, sort_criteria = 'file', view_max_file_count = -1)
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
	"""
	all_files = _files_gen(db, args.drives, args.exclude_drives)
	verbose = args.quiet < 2
		
	# file_size_threshold
	seuil = args.file_size_threshold
	if seuil > 0:
		func = lambda (root, file, size): size >= seuil
		all_files = itertools.ifilter(func, all_files)
		if verbose: print 'Files smaller than', hr_size(seuil), 'are ignored.'
	
	# group by filename
	group_key = lambda (root, file, size): file
	
	if ignore_case:
		# ignore case
		key = group_key
		group_key = lambda file: key(file).lower()
	
	all_files = sorted(all_files, key=group_key)
	c_all = len(all_files)
	
	doublons = []
	filenames_count = 0
	duplicates_filenames_count = 0
	for k, g in itertools.groupby(all_files, group_key):
		filenames_count += 1
		r_s = map(lambda (root, file, size): (root, size), g)
		if len(r_s) > 1:
			duplicates_filenames_count += 1
			doublon = tuple([k] + zip(*r_s))
			doublons.append(doublon)
	del all_files
		
	if verbose:
		print 'Count of filenames :', filenames_count
		if filenames_count:
			print 'Noms de fichiers non uniques :', duplicates_filenames_count
	
	if duplicates_filenames_count == 0:
		if verbose: print 'Aucun doublon trouve.'
	else:
		
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
			print u'Tuples de répertoires contenant des fichiers de même nom :', directory_tuples_count
			if seuil >= 2:
				print u'Tuples de répertoires contenant plus de', seuil, u'fichiers de même nom :', final_directory_tuples_count
		
		# filtre 1 : enlève les résultats contenant plus de trois fichiers et dont les noms de fichiers (tous)
		#            sont identiques à l'exception des éventuels caractères numériques (0-9)
		if args.filter and 1 in args.filter:
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

		if args.sort_criteria == 'directory':
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
		elif args.sort_criteria == 'file':
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
