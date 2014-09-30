CGIShell
========

* [shellshock](https://shellshocker.net/)
* CVE-2014-6271 CGI Exploit
* Use like OpenSSH via CGI Page

Use
===

`python cgishell.py 'http://www.google.com/cve-2014-6271/poc.cgi'`


Screenshot
==========

![Success](http://i.v2ex.co/5sVSEz4Yl.png "")

Dependence
==========

* Windows needed `pyreadline`
* It is not needed `chardet`

Future
======

* Add TestCase
* HTTP Login Support
* http transmission gzip compression
* chardet identify and decode
* any bug fix

Issues
======

* Windows Untest
