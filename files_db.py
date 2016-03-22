# -*- coding: utf8 -*-
"""
FilesDb class
"""

from os.path import join, getsize
import os, pickle, string

class FilesDb:
	def __init__(self, exclude_drives=('C',), db_filepath=None):
		"""
		>>> db = FilesDb()
		>>> print ' '.join(db.exclude_drives)
		C
		>>> print db.db_filepath
		None
		>>> db.size_not_found
		[]
		>>> db._db
		{}
		"""
		if exclude_drives is None: exclude_drives = ''
		self.exclude_drives = exclude_drives
		self.db_filepath = db_filepath
		self._init_db()
		self.size_not_found = []
		
	#def _add_fake_file(self, drive, file=None, size=None):
	#	""" add fake file in database for test purpose only
	#	>>> FilesDb()._add_fake_file('A')._add_fake_file('A').len('A')
	#	2
	#	"""
	#	if drive not in self._db: self._db[drive] = []
	#	files = self._db[drive]
	#	if file is None:
	#		if files: i = int(files[-1][1].split()[1]) + 1
	#		else: i = 1
	#		file = 'file {}'.format(i)
	#	if size is None: size = 0
	#	files.append(( join(drive+':/', 'dir'), file, size ))
	#	return self
		
	def _init_db(self):
		"""
		>>> db = FilesDb()
		>>> db._init_db()
		>>> db._db = 'toto'
		>>> db._init_db()
		>>> db._db
		{}
		>>> db._db = dict(A='toto')
		>>> db._init_db()
		>>> db._db
		{}
		"""
		self._db = dict()
		
	def __len__(self):
		""" database file count
		>>> len(FilesDb())
		0
		>>> len(testdb)
		9
		"""
		return self.len()
	
	def len(self, drive=None):
		""" file count of database or drive
		>>> FilesDb().len('X')
		0
		>>> testdb.len(drive1)
		5
		"""
		if drive is None: return sum([len(files) for files in self._db.itervalues()])
		elif len(drive) == 1 and drive in self._db: return len(self._db[drive])
		else: return 0
		
	def load(self):
		""" load database from self.db_filepath using pickle -> count of file entries loaded
		>>> FilesDb().load()
		0
		>>> fd, path = tempfile.mkstemp()
		>>> os.close(fd)
		>>> testdb.db_filepath = path
		>>> testdb.save()
		True
		>>> FilesDb(db_filepath=path).load()
		9
		>>> os.remove(path)
		"""
		if self.db_filepath is None: return 0
		try:
			with open(self.db_filepath, 'rb') as file:
				db = pickle.load(file)
			self._db = db
			return len(self)
		except:
			return 0

	def save(self):
		""" save database in self.db_filepath using pickle -> success (boolean)
		>>> FilesDb().save()
		False
		>>> fd, path = tempfile.mkstemp()
		>>> os.close(fd)
		>>> testdb.db_filepath = path
		>>> testdb.save()
		True
		>>> os.remove(path)
		"""
		if self.db_filepath is None: return False
		try:
			with open(self.db_filepath, 'wb') as file:
				pickle.dump(self._db, file, -1)
			return True
		except:
			return False
		
	def clear(self, drive=None):
		""" clear database or drive -> success (boolean)
		>>> db = FilesDb()
		>>> db.clear()
		True
		>>> db.clear('A')
		False
		>>> db._db = dict(A=[('', '', 0), ('', '', 0)], B=[('', '', 0)])
		>>> len(db)
		3
		>>> db.clear('A')
		True
		>>> len(db)
		1
		>>> db.clear()
		True
		>>> len(db)
		0
		"""
		if drive is None: self._init_db()
		elif len(drive) == 1 and drive in self._db: del self._db[drive]
		else: return False
		return True
		
	def drives(self):
		""" sorted copy of database drives list
		>>> FilesDb().drives()
		[]
		>>> testdb.drives() == sorted([drive1, drive2])
		True
		"""
		return sorted(self._db.iterkeys())
				
	def files(self, drive=None):
		r""" generator on stored files
		>>> for root, file, size in testdb.files():
		... 	print root[1:11]
		:\0_Tout e
		:\1_L'amou
		:\2_Ils n'
		:\3_Et leu
		:\
		:\0_Votre 
		:\1_Que vo
		:\2_Jouant
		:\3_Triste
		>>> for root, file, size in testdb.files(drive2):
		... 	print root[1:11]
		:\0_Tout e
		:\1_L'amou
		:\2_Ils n'
		:\3_Et leu
		"""
		drives = self.drives()
		if drive != None:
			if drive in drives: drives = [drive]
			else: drives = []
		for d in sorted(drives):
			for file in self._db[d]:
				yield file
				
	def size(self, drive=None):
		""" sum of stored files size
		>>> print testdb.size(), testdb.size(drive1), testdb.size(drive2)
		13 13 0
		"""
		s = 0
		for root, file, size in self.files(drive):
			s += size
		return s
				
	def _get_drives(self):
		""" system drives which are not in self.exclude_drives
		>>> db = FilesDb(exclude_drives='')
		>>> drives = db._get_drives()
		>>> len(drives) >= 1
		True
		>>> db.exclude_drives = drives
		>>> db._get_drives()
		[]
		"""
		return [c for c in string.ascii_uppercase if c not in self.exclude_drives and os.path.isdir(c+':/')]

	def _scan_drive_gen(self, drive):
		r""" 
		>>> db = FilesDb()
		>>> for root, file, size in db._scan_drive_gen(drive1):
		... 	print root.replace('â'.decode('utf8'), 'A').replace('é'.decode('utf8'), 'E')[1:], file, size
		:\ titre.txt 13
		:\0_Votre Ame\est un\ paysage choisi 0
		:\1_Que vont\charmant masques et bergamasques 0
		:\2_Jouant du luth\et dansant  et quasi 0
		:\3_Tristes\sous leurs dEguisements  fantasques._ 0
		"""
		for root, dirs, files in os.walk(drive + u':\\'):
			for file in files:
				path = join(root, file)
				try:
					size = getsize(path)
				except:
					self.size_not_found.append(path)
					size = 0
				yield (root, file, size)
				
	def update_drives_gen(self, drives):
		r"""
		>>> db = FilesDb()
		>>> for root, file, size in db.update_drives_gen(drive1+drive2):
		... 	print root.replace('â'.decode('utf8'), 'A1').replace('é'.decode('utf8'), 'E1').replace('ê'.decode('utf8'), 'E2')[1:],
		... 	print '-', file.replace('à'.decode('utf8'), 'A2'), size
		:\ - titre.txt 13
		:\0_Votre A1me\est un\ paysage - choisi 0
		:\1_Que vont\charmant masques - et bergamasques 0
		:\2_Jouant du luth\et dansant -  et quasi 0
		:\3_Tristes\sous leurs dE1guisements -  fantasques._ 0
		:\0_Tout en chantant - sur le mode.mineur 0
		:\1_L'amour\vainqueur\et la vie - opportune 0
		:\2_Ils n'ont pas\l'air de croire - A2 leur bonheur 0
		:\3_Et leur chanson\se mE2le - au clair de lune, 0
		>>> db.drives() == [drive2, drive1]
		True
		>>> db.len(drive2)
		4
		"""
		for drive in drives:
			first = True
			for file in self._scan_drive_gen(drive):
				if first:
					self._db[drive] = []
					first = False
				self._db[drive].append(file)
				yield file
			
	def update_drives(self, drives):
		r"""
		>>> db = FilesDb()
		>>> db.update_drives(drive1+drive2)
		9
		>>> print db.size(drive1)
		13
		"""
		self.size_not_found = []
		c = 0
		for file in self.update_drives_gen(drives): c += 1
		return c

	def update_gen(self):
		"""
		>>> db = FilesDb(exclude_drives=testdb.exclude_drives)
		>>> for size in sorted([size for root, file, size in db.update_gen()]):
		... 	print size,
		0 0 0 0 0 0 0 0 13
		"""
		self.size_not_found = []
		drives = self._get_drives()
		for file in self.update_drives_gen(drives):
			yield file
			
	def update(self):
		"""
		>>> db = FilesDb(exclude_drives=testdb.exclude_drives)
		>>> db.update()
		9
		"""
		c = 0
		for file in self.update_gen(): c += 1
		return c
		
	# input : can contain '*' to enlarge search
	def find(self, input, ignore_case=False): # -> [ ( root, file, size ), ... ]
		r"""
		>>> for root, file, size in testdb.find('*._'):
		... 	print file
		 fantasques._
		>>> for root, file, size in sorted(testdb.find(' *')):
		... 	print file
		 et quasi
		 fantasques._
		>>> for root, file, size in sorted(testdb.find('*de*')):
		... 	print file
		sur le mode.mineur
		au clair de lune,
		>>> len(testdb.find('*'))
		9
		"""
		if not input: return []
		if ignore_case: elmts = input.lower().split('*')
		else: elmts = input.split('*')
		simple = len(elmts) == 1
		if not simple:
			debut = elmts.pop(0)
			debut = len(debut), debut
			fin = elmts.pop()
			fin = len(fin), fin
		matches = []
		for root, file, size in self.files():
			if ignore_case: cmp_str = file.lower()
			else: cmp_str = file
			if simple:
				if elmts[0] == cmp_str:
					matches.append((root, file, size))
				continue
			i0 = 0
			if debut[0] and cmp_str[:debut[0]] != debut[1]: continue
			else: i0 += debut[0]
			i1 = len(cmp_str)
			if fin[0] and cmp_str[-fin[0]:] != fin[1]: continue
			else: i1 -= fin[0]
			stop = False
			for elmt in elmts:
				if elmt not in cmp_str[i0:i1]:
					stop = True
					break
				else:
					i0 = cmp_str.index(elmt, i0) + len(elmt)
			if elmts and stop: continue
			matches.append((root, file, size))
		return matches

if __name__ == "__main__":
	import doctest, tempfile
	import files_db_test as test
	drive1, drive2, updated_db, sav = test.files_db_context_build(FilesDb())
	doctest.testmod(
		name='files_db',
		extraglobs=dict(drive1=drive1, drive2=drive2, testdb=updated_db),
		optionflags=doctest.REPORT_ONLY_FIRST_FAILURE # | doctest.REPORT_UDIFF
		)
	test.context_del((drive1,drive2), sav)
