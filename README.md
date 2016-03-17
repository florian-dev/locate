# locate
Locate files using a simple managed database. Can find a file name pattern and seek for duplicates files.

Written for Windows. On Linux updatedb and locate commands do the job (except for duplicates seek), and I don't know MacOs.

TODO :
- [x] add --clean-drives option to updatedb action
- [ ] using filters for find action (ex: file-size-threshold)

###### locate.py -h :
```
usage: locate.py [-h] {find,updatedb,duplicates} ...

locate files in a managed database

optional arguments:
  -h, --help            show this help message and exit

commands:
  {find,updatedb,duplicates}
    find                find files in database
    updatedb            update database
    duplicates          find duplicate files in database
```

###### locate.py find -h :
```
usage: locate.py find [options] pattern

find files in database

positional arguments:
  pattern               filname pattern to search for. It can contain '*'

optional arguments:
  -h, --help            show this help message and exit
  -i, --ignore-case
  -t <file_size>, --file-size-threshold <file_size>
                        File size threshold (smaller ones are ignored).
                        (default: 0)

general options:
  -p <path>, --db-filepath <path>
                        files database file path (default: c:/files.db)
  -d <drives>, --drives <drives>
                        restrict action to some drives (default: None)
  -x [<drives>], --exclude-drives [<drives>]
                        do not update or use data for these drives (default:
                        C)
  -u, --updatedb        update files database before processing (default:
                        False)
  -l <log_file>, --log-file <log_file>
                        use <log_file> as main output with utf8 encoding and
                        convert stdout to 'replace' mode if --no-stdout is not
                        present. (default: None)
  -n, --no-stdout
  -q, --quiet

<drives>    : (<letter>[:])+        Example: 'dE:h:Gp'
<file_size> : <integer>[kMGT][B]    Example: '500kB'
```

###### locate.py update -h :
```
###### locate.py -h :
```
usage: locate.py [-h] {find,updatedb,duplicates} ...

locate files in a managed database

optional arguments:
  -h, --help            show this help message and exit

commands:
  {find,updatedb,duplicates}
    find                find files in database
    updatedb            update database
    duplicates          find duplicate files in database
```

###### locate.py find -h :
```
usage: locate.py find [options] pattern

find files in database

positional arguments:
  pattern               filname pattern to search for. It can contain '*'

optional arguments:
  -h, --help            show this help message and exit
  -i, --ignore-case
  -t <file_size>, --file-size-threshold <file_size>
                        File size threshold (smaller ones are ignored).
                        (default: 0)

general options:
  -p <path>, --db-filepath <path>
                        files database file path (default: c:/files.db)
  -d <drives>, --drives <drives>
                        restrict action to some drives (default: None)
  -x [<drives>], --exclude-drives [<drives>]
                        do not update or use data for these drives (default:
                        C)
  -u, --updatedb        update files database before processing (default:
                        False)
  -l <log_file>, --log-file <log_file>
                        use <log_file> as main output with utf8 encoding and
                        convert stdout to 'replace' mode if --no-stdout is not
                        present. (default: None)
  -n, --no-stdout
  -q, --quiet

<drives>    : (<letter>[:])+        Example: 'dE:h:Gp'
<file_size> : <integer>[kMGT][B]    Example: '500kB'
```

###### locate.py updatedb -h :
```
usage: locate.py updatedb [options]

update database

optional arguments:
  -h, --help            show this help message and exit
  -r, --repport         print database repport (default: False)
  -c <drives>, --clean-drives <drives>
                        clean data for these drives before update (default:
                        None)

general options:
  -p <path>, --db-filepath <path>
                        files database file path (default: c:/files.db)
  -d <drives>, --drives <drives>
                        restrict action to some drives (default: None)
  -x [<drives>], --exclude-drives [<drives>]
                        do not update or use data for these drives (default:
                        C)
  -u, --updatedb        update files database before processing (default:
                        False)
  -l <log_file>, --log-file <log_file>
                        use <log_file> as main output with utf8 encoding and
                        convert stdout to 'replace' mode if --no-stdout is not
                        present. (default: None)
  -n, --no-stdout
  -q, --quiet

<drives>    : (<letter>[:])+        Example: 'dE:h:Gp'
```

###### locate.py duplicates -h :
```
usage: locate.py duplicates [options]

find duplicate files in database

optional arguments:
  -h, --help            show this help message and exit
  -t [<file_size>], --file-size-threshold [<file_size>]
                        File size threshold (smaller ones are ignored).
                        (implicit value: 2MB) (default: 0)
  -s {file,directory}, --sort-criteria {file,directory}
                        Sort criteria : 'file' (default) = by decreasing file
                        count ; 'directory' = by decreasing directories count,
                        then by directories names (default: file)
  -m [<count>], --min-file-count [<count>]
                        Exclude results with less than <count> duplicate
                        files. (implicit value: 6) (default: 1)
  -v [<count>], --view-max-file-count [<count>]
                        Print only first <count> file(s) per result. (implicit
                        value: 15) (default: -1)
  -f, --filter-01       filter 1 : ignore results with more than three files
                        and whose all filenames are same except for digits
                        characters (0-9) (default: False)

general options:
  -p <path>, --db-filepath <path>
                        files database file path (default: c:/files.db)
  -d <drives>, --drives <drives>
                        restrict action to some drives (default: None)
  -x [<drives>], --exclude-drives [<drives>]
                        do not update or use data for these drives (default:
                        C)
  -u, --updatedb        update files database before processing (default:
                        False)
  -l <log_file>, --log-file <log_file>
                        use <log_file> as main output with utf8 encoding and
                        convert stdout to 'replace' mode if --no-stdout is not
                        present. (default: None)
  -n, --no-stdout
  -q, --quiet

<drives>    : (<letter>[:])+        Example: 'dE:h:Gp'
<file_size> : <integer>[kMGT][B]    Example: '500kB'
```

