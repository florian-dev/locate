# locate
Locate files using a simple managed database. Can find a file name pattern and seek for duplicates files.

TODO :
	add --db-filepath option
	add --exclude-drives option to updatedb action
	code refactoring
	using filters before find (ex: file-size-threshold)
	more...

------------------------------------------------------------

usage: locate.py [-h] [-u] [-l <log_file>] [-n] [-q]
                 {find,updatedb,duplicates} ...

locate files in a managed database

positional arguments:
  {find,updatedb,duplicates}
    find                find files in database
    updatedb            update database
    duplicates          find duplicate files in database

optional arguments:
  -h, --help            show this help message and exit
  -u, --updatedb        update files database before processing
  -l <log_file>, --log-file <log_file>
                        use <log_file> as main output with utf8 encoding and
                        convert stdout to 'replace' mode if --no-stdout is not
                        present.
  -n, --no-stdout
  -q, --quiet

--------------------------- find ---------------------------

usage: locate.py find [-h] [-i] pattern

positional arguments:
  pattern

optional arguments:
  -h, --help         show this help message and exit
  -i, --ignore-case

------------------------- updatedb -------------------------

usage: locate.py updatedb [-h] [-r]

optional arguments:
  -h, --help            show this help message and exit
  -r, --repport-total-size
                        print sum of all files size in database

------------------------ duplicates ------------------------

usage: locate.py duplicates [-h] [-t [<file_size>]] [-d] [-m [<count>]]
                            [-v [<count>]] [-f]

optional arguments:
  -h, --help            show this help message and exit
  -t [<file_size>], --file-size-threshold [<file_size>]
                        File size threshold (smaller ones are ignored).
                        <file_size> syntax is '<integer>[kMGT][B]'. Example:
                        '500kB' (default: 2MB)
  -d, --directory-sorting
                        Sort by decreasing directories count, then by
                        directories names. Default sort is by decreasing file
                        count.
  -m [<count>], --min-file-count [<count>]
                        Exclude results with less than <count> duplicate
                        files. (default: 6)
  -v [<count>], --view-max-file-count [<count>]
                        Print only first <count> file(s) per result. (default:
                        15)
  -f, --filter-01       filter 1 : ignore results with more than three files
                        and whose all filenames are same except for digits
                        characters (0-9)

						
						