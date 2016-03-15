# -*- coding: utf8 -*-
from os.path import join, getsize
from time import time
import os, pickle, string

class FilesDb:
	def __init__(self, exclude_drives=('C',), db_filepath='c:/files.db'):
		self.exclude_drives = exclude_drives
		self.db_filepath = db_filepath
		self._init_db()
		self.size_not_found = []
		
	def _init_db(self):
		self._db = dict()
		
	def __len__(self):
		return sum([len(files) for files in self._db.itervalues()])
		
	def load(self): # -> count of file entries loaded
		try:
			with open(self.db_filepath, 'rb') as file:
				db = pickle.load(file)
			self._db = db
			return len(self)
		except:
			return 0

	def save(self): # -> boolean
		try:
			with open(self.db_filepath, 'wb') as file:
				pickle.dump(self._db, file, -1)
			return True
		except:
			return False
		
	def clear(self): # clear db
		self._init_db()
		
	def drives(self): # -> [ drive, ... ]
		#return [drive for drive, files in self._db]
		return sorted(self._db.iterkeys())
				
	def files(self): # -> [ ( root, file, size ), ... ]
		for drive in self.drives():
			for file in self._db[drive]:
				yield file
				
	def size(self):
		s = 0
		for root, file, size in self.files():
			s += size
		return s
				
	def _get_drives(self):
		return [c for c in string.uppercase if c not in self.exclude_drives and os.path.isdir(c+':/')]

	def _scan_drive_gen(self, drive):
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
		for drive in drives:
			first = True
			for file in self._scan_drive_gen(drive):
				if first:
					self._db[drive] = []
					first = False
				self._db[drive].append(file)
				yield file
			
	def update_drives(self, drives):
		self.size_not_found = []
		c = 0
		for file in self.update_drives_gen(drives): c += 1
		return c

	def update_gen(self):
		self.size_not_found = []
		drives = self._get_drives()
		for file in self.update_drives_gen(drives):
			yield file
			
	def update(self):
		c = 0
		for file in self.update_gen(): c += 1
		return c
		
	# input : can contain '*' to enlarge search
	def find(self, input, ignore_case=False): # -> [ ( root, file, size ), ... ]
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
