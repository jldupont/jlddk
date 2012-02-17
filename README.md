For more information, visit http://www.systemical.com/doc/opensource/jlddk


History
=======

0.1.22 :

* added requirement for 'init' function in tools_flow


0.1.20 :

* added 'jldclock'
* added 'tools_flow' module

0.1.12 :

* added "jldfilelist"

0.1.11 :

* added 'jldfetcher'
* fixed output buffering issue (again)

0.1.10 : removed output buffering on stdout

0.1.9 :

* fixed 'lc' option present in most scripts
* added 'jldinotify'

0.1.8 : added parameters & better error handling to jldfilter 

0.1.7 : added stdout.flush() to jldwebscraper

0.1.6 :

* Added 'batch size' option to jldwebscraper (having problems with stdout buffering)

0.1.5 :

* Added 'jldcomp' script
* New dependency : 'pyfnc' package

0.1.4 : 

* Updated 'jldwebdl' to use 'atomic_write' for creating the destination file(s)
* Updated 'jldwebscraper', 'jldjsoncat' & 'jldwebdl': gate operation using the existence of a specified filesystem path
* Fixed bug in 'jldjsoncat'
