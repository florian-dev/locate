# locate
Locate files using a simple managed database. Can find a file name pattern and seek for duplicates files.

Written for Windows. On Linux updatedb and locate commands do the job (except for duplicates seek), and I don't know MacOs.

TODO :
- [x] add --clean-drives option to updatedb action
- [ ] using filters for find action (ex: file-size-threshold)

###### locate.py -h :
```
usage: locate.py [-h] [-d <path>] [--drives <drives>] [-x [<drives>]] [-u]
                 [-l <log_file>] [-n] [-q]
                 {find,updatedb,duplicates} ...

locate files in a managed database

positional arguments:
  {find,updatedb,duplicates}
    find                find files in database
    updatedb            update database
    duplicates          find duplicate files in database

optional arguments:
  -h, --help            show this help message and exit
  -d <path>, --db-filepath <path>
                        files database file path
  --drives <drives>     restrict action to some drives (ex: '--drives
                        dE:h:Gp') ('x:' = 'x' = 'X' = 'X:')
  -x [<drives>], --exclude-drives [<drives>]
                        do not update or use data for these drives (default:
                        C)
  -u, --updatedb        update files database before processing
  -l <log_file>, --log-file <log_file>
                        use <log_file> as main output with utf8 encoding and
                        convert stdout to 'replace' mode if --no-stdout is not
                        present.
  -n, --no-stdout
  -q, --quiet
```

###### locate.py find -h :
```
usage: locate.py find [-h] [-i] pattern

positional arguments:
  pattern

optional arguments:
  -h, --help         show this help message and exit
  -i, --ignore-case
```

###### locate.py updatedb -h :
```
usage: locate.py updatedb [-h] [-r] [-c <drives>]

optional arguments:
  -h, --help            show this help message and exit
  -r, --repport         print database repport
  -c <drives>, --clean-drives <drives>
                        clean data for these drives before update
```

###### locate.py duplicates -h :
```
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
```

