# locate
Locate files using a simple managed database. Can find a file name pattern and seek for duplicates files. (Python 2.7 - Windows - unicode filenames support)

Written for Windows. On Linux updatedb and locate commands do the job (except for duplicates seek), and I don't know MacOs.

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
  pattern               filname pattern to search for ; pattern can contain
                        '*' to widen results

general options:
  -p <path>, --db-filepath <path>
                        files database file path (default:
                        ~/files_db_default_file.db)
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
                        present (default: None)
  -i, --ignore-case     useless with updatedb command (default: False)
  -n, --no-stdout
  -q, --quiet

find options:
  -h, --help            show this help message and exit
  -w, --wide            transform 'pattern' to '*pattern*' (default: False)
  -t <file_size>, --file-size-threshold <file_size>
                        file size threshold (smaller ones are ignored)
                        (default: 0)

<drives>    : (<letter>[:])+        Example: 'dE:h:Gp'
<file_size> : <integer>[kMGT][B]    Example: '500kB'
```

###### locate.py updatedb -h :
```
usage: locate.py updatedb [options]

update database

general options:
  -p <path>, --db-filepath <path>
                        files database file path (default:
                        ~/files_db_default_file.db)
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
                        present (default: None)
  -i, --ignore-case     useless with updatedb command (default: False)
  -n, --no-stdout
  -q, --quiet

updatedb options:
  -h, --help            show this help message and exit
  -r, --repport         print database repport (default: False)
  -c <drives>, --clean-drives <drives>
                        clean data for these drives (before update) (default:
                        None)

<drives>    : (<letter>[:])+        Example: 'dE:h:Gp'
```

###### locate.py duplicates -h :
```
usage: locate.py duplicates [options]

find duplicate files in database

general options:
  -p <path>, --db-filepath <path>
                        files database file path (default:
                        ~/files_db_default_file.db)
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
                        present (default: None)
  -i, --ignore-case     useless with updatedb command (default: False)
  -n, --no-stdout
  -q, --quiet

duplicates options:
  -h, --help            show this help message and exit
  -e, --check-exact-filesize
                        check filename and filesize (default: False)
  -a, --check-approximative-filesize
                        check filename and filesize (default: False)
  -s {file,directory}, --sort-criteria {file,directory}
                        sort criteria : 'file' (default) = by decreasing file
                        count ; 'directory' = by decreasing directories count,
                        then by directories names (default: file)
  -v [<count>], --view-max-file-count [<count>]
                        print only first <count> file(s) per result (implicit
                        value: 15) (default: -1)

filters:
  filter  1 :  ignore results with more than three files and whose all
               filenames are same except for digits characters (0-9)
  filter  2 :  ignore results with more than one file and whose all
               filenames are same except for digits characters (0-9)

  -f {1,2,3}, --filter {1,2,3}
                        apply one filter among those listed above ; this
                        option can be mentioned several times (default: None)
  -t [<file_size>], --file-size-threshold [<file_size>]
                        file size threshold (smaller ones are ignored)
                        (implicit value: 2MB) (default: 0)
  -m [<count>], --min-file-count [<count>]
                        exclude results with less than <count> duplicate files
                        (implicit value: 6) (default: 1)

<drives>    : (<letter>[:])+        Example: 'dE:h:Gp'
<file_size> : <integer>[kMGT][B]    Example: '500kB'
```

