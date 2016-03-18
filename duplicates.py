# -*- coding: utf8 -*-

from common import hr_size

def _files_gen(db, drives, exclude_drives):
	if drives is None: drives = db.drives()
	if exclude_drives: drives = [drive for drive in drives if drive not in exclude_drives]
	for drive in drives:
		for file in db.files(drive):
			yield file

def duplicates(db, args):
	verbose = args.quiet < 2
	all_files = sorted(_files_gen(db, args.drives, args.exclude_drives), key=lambda item: item[1])
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

	if verbose and seuil: print 'Files smaller than', hr_size(seuil), 'are ignored.'
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
			
