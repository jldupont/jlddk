For more information, visit http://www.systemical.com/doc/opensource/jlddk


History
=======

0.7.36: added 'dp' option to jldcomp

0.7.34: added 'jlddirzip'

0.7.32: added 'jldbolus'

0.7.24: extended 'ipat' option on jldsplitter

0.7.22: fixed pclean: caching of ppid value in psutil package caused malfunction

0.7.18: small fix for pclean

0.7.9: added support for 'syslog'

0.7.1: added ctx (context data) to jldarun

0.7.0: added "jldarun"

0.6.5: added "jldsplitter"

0.6.3: added support for 'init' function in jldfilter

0.6.0: standardized log parameters, fixed bug in jldclock

0.5.1: added new options to jldclock

0.5.0: added 'jldstrpkg' and version # to all scripts

0.4.22: added debug utils in 'jlddk.utils'

0.4.2: added "jldrun"

0.3.0: added 'jldstatsubdirs'

0.2.8: added 'tp' option to jldcomp

0.2.7: added 'jbn' option to jldcomp

0.2.6 : added 'check path' option to jldcomp

0.2.5 : added "jldostr" script

0.2.4 : added a "stdin-->stdout" pass-through to jldwebdl

0.2.0 : 

* added "jldtaskctl"
* fixed broken pipe detection in "jldclock"
* better broken pipe handling

0.1.23: added protection against parent termination & broken pipe condition

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
